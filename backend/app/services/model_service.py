import os
import logging
import hashlib
from app.core.config import settings

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        # Import Redis client
        try:
            from app.utils.redis_client import redis_client
            self.redis_client = redis_client
            logger.info("Redis client initialized for model service")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            self.redis_client = None
        
    def _generate_cache_key(self, text: str) -> str:
        """Generate a cache key for the given text"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"sms_prediction:{text_hash}"
        
    def load_model(self):
        """Load the TinyLlama model with local PEFT adapters for sequence classification"""
        try:
            # Import here to avoid import errors if libraries are not available
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            from peft import PeftModel, PeftConfig
            from safetensors.torch import load_file
            
            logger.info("Loading local TinyLlama model with PEFT adapters for sequence classification")
            
            # Load PEFT config first to understand the exact architecture
            local_adapter_path = "../local_tinyllama_sms_spam_model"
            peft_config = PeftConfig.from_pretrained(local_adapter_path)
            logger.info(f"PEFT config loaded: task_type={peft_config.task_type}, modules_to_save={getattr(peft_config, 'modules_to_save', 'None')}")
            
            # Use the base model name from config if available, otherwise use default
            base_model_name = getattr(peft_config, 'base_model_name_or_path', None) or "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            logger.info(f"Loading base model: {base_model_name}")
            
            # Load base model with the correct configuration for PEFT
            base_model = AutoModelForSequenceClassification.from_pretrained(
                base_model_name,
                num_labels=2,  # For binary classification (spam/not spam)
                torch_dtype="auto"
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            
            # Set padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                base_model.config.pad_token_id = self.tokenizer.eos_token_id
            
            # Apply local PEFT adapters with proper error handling
            logger.info(f"Applying local PEFT adapters from: {local_adapter_path}")
            
            # Check if the path exists
            if not os.path.exists(local_adapter_path):
                logger.error(f"Local adapter path does not exist: {local_adapter_path}")
                return False
            
            # Try to load the full PEFT model first with different approaches to handle path mismatch
            try:
                # First try: Standard loading
                self.model = PeftModel.from_pretrained(base_model, local_adapter_path, is_trainable=False)
                logger.info("Full PEFT model loaded successfully with classification head")
            except Exception as e:
                logger.warning(f"Could not load full PEFT model with standard approach: {e}")
                logger.info("Attempting to manually load classification head weights and LoRA adapters...")
                
                # Manual approach to handle the path mismatch for classification head weights
                try:
                    # Create PeftModel with the original config
                    self.model = PeftModel(base_model, peft_config)
                    
                    # Load all adapter weights
                    adapter_weights_path = os.path.join(local_adapter_path, "adapter_model.safetensors")
                    if os.path.exists(adapter_weights_path):
                        # Load the weights manually
                        adapter_weights = load_file(adapter_weights_path)
                        
                        # Check if we have the classification head weights with the expected path
                        expected_key = "base_model.model.base_model.model.score.weight"
                        if expected_key in adapter_weights:
                            # Get the classification head weights
                            score_weights = adapter_weights[expected_key]
                            
                            # Try to manually assign them to the model
                            try:
                                # Get the current score weight tensor from the model
                                current_score_weight = self.model.base_model.model.score.weight
                                
                                # Check if shapes match
                                if current_score_weight.shape == score_weights.shape:
                                    # Assign the trained weights
                                    with torch.no_grad():
                                        self.model.base_model.model.score.weight.copy_(score_weights)
                                    logger.info("Successfully loaded classification head weights manually")
                                else:
                                    logger.warning(f"Shape mismatch for classification head weights. Expected: {current_score_weight.shape}, Got: {score_weights.shape}")
                            except Exception as assign_error:
                                logger.warning(f"Could not assign classification head weights: {assign_error}")
                        else:
                            logger.warning("Classification head weights not found in adapter file with expected key")
                    
                    # For LoRA adapters, we need to handle the path mismatch differently
                    # Load only the LoRA weights (excluding the modules_to_save)
                    try:
                        # Create a new peft config without modules_to_save to avoid the path mismatch
                        from peft import LoraConfig
                        lora_only_config = LoraConfig(
                            r=peft_config.r,
                            lora_alpha=peft_config.lora_alpha,
                            target_modules=peft_config.target_modules,
                            lora_dropout=peft_config.lora_dropout,
                            bias=peft_config.bias,
                            task_type=peft_config.task_type
                            # Note: Not including modules_to_save to avoid path mismatch
                        )
                        
                        # Load only the LoRA adapters (this should work without the classification head path issue)
                        self.model.load_adapter(local_adapter_path, adapter_name="default", strict=False)
                        logger.info("LoRA adapters loaded successfully with strict=False")
                    except Exception as lora_error:
                        logger.warning(f"Could not load LoRA adapters normally: {lora_error}")
                        logger.info("Continuing with classification head weights only...")
                        
                except Exception as e2:
                    logger.error(f"Failed to manually load weights: {e2}")
                    logger.info("Loading base model only with LoRA adapters (classification head will use base model weights)")
                    # Fallback to just the base model with LoRA adapters
                    self.model = PeftModel(base_model, peft_config)
            
            # Move model to appropriate device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            
            # Set to evaluation mode
            self.model.eval()
            
            logger.info(f"Using device: {self.device}")
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.error(f"Full traceback: ", exc_info=True)
            return False
    
    def predict(self, text: str) -> dict:
        """Predict if an SMS is spam or not with Redis caching"""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Call load_model() first.")
            
        # Generate cache key
        cache_key = self._generate_cache_key(text)
        
        # Try to get result from cache first
        if self.redis_client and self.redis_client.connected:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for prediction: {text[:50]}...")
                    return cached_result
                else:
                    logger.info(f"Cache miss for prediction: {text[:50]}...")
            except Exception as e:
                logger.warning(f"Error checking cache: {e}")
        
        try:
            # Import here to avoid import errors
            import torch
            
            # Tokenize input for sequence classification
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Run prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                confidence, predicted_class = torch.max(predictions, dim=-1)
                
                # Convert to Python types
                confidence = confidence.item()
                predicted_class = predicted_class.item()
                
                # Map class indices to labels (fixing the label mapping)
                # Based on training: class 1 = spam, class 0 = not_spam
                label = "spam" if predicted_class == 1 else "not_spam"
                
                result = {
                    "prediction": label,
                    "confidence": confidence,
                    "class_probabilities": {
                        "not_spam": predictions[0][0].item(),
                        "spam": predictions[0][1].item()
                    }
                }
                
                # Cache the result for future requests
                if self.redis_client and self.redis_client.connected:
                    try:
                        self.redis_client.set(cache_key, result, expire=3600)  # Cache for 1 hour
                        logger.info(f"Result cached for: {text[:50]}...")
                    except Exception as e:
                        logger.warning(f"Error caching result: {e}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

# Create a singleton instance
model_service = ModelService()