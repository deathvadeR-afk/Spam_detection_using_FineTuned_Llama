import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class InputValidator:
    """Utility class for validating and sanitizing user inputs"""
    
    # Patterns for detecting potentially malicious input
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|\/\*|\*\/|;)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>"
    ]
    
    # SMS-specific validation
    SMS_MAX_LENGTH = 1000  # Maximum length for SMS text
    
    @classmethod
    def sanitize_sms_text(cls, text: str) -> str:
        """
        Sanitize SMS text by removing or escaping potentially harmful content
        
        Args:
            text: SMS text to sanitize
            
        Returns:
            Sanitized SMS text
        """
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limit length
        if len(text) > cls.SMS_MAX_LENGTH:
            text = text[:cls.SMS_MAX_LENGTH]
            
        return text
    
    @classmethod
    def validate_sms_text(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SMS text for security issues
        
        Args:
            text: SMS text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "SMS text cannot be empty"
            
        # Check length
        if len(text) > cls.SMS_MAX_LENGTH:
            return False, f"SMS text too long (max {cls.SMS_MAX_LENGTH} characters)"
            
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected in SMS text: {text[:50]}...")
                return False, "Invalid characters detected in SMS text"
                
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential XSS detected in SMS text: {text[:50]}...")
                return False, "Invalid characters detected in SMS text"
                
        return True, None
    
    @classmethod
    def validate_batch_sms_texts(cls, texts: list) -> Tuple[bool, Optional[str]]:
        """
        Validate a batch of SMS texts
        
        Args:
            texts: List of SMS texts to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not texts:
            return False, "SMS texts list cannot be empty"
            
        if len(texts) > 1000:  # Limit batch size
            return False, "Too many SMS texts in batch (max 1000)"
            
        for i, text in enumerate(texts):
            is_valid, error_msg = cls.validate_sms_text(text)
            if not is_valid:
                return False, f"Invalid SMS text at position {i}: {error_msg}"
                
        return True, None

# Create a global validator instance
validator = InputValidator()