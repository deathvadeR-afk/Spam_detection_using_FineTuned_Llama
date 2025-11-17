# TinyLlama SMS Spam Detection Application

A production-grade application for detecting SMS spam using a fine-tuned TinyLlama-1.1B model with PEFT (LoRA/QLoRA) techniques.

## Overview

This project demonstrates how to build a complete AI application around a fine-tuned language model for SMS spam classification. The model achieves 98% test accuracy while training only 0.22% of parameters, making it highly efficient for production deployment.

## Features

- **AI-Powered Spam Detection**: Uses a fine-tuned TinyLlama-1.1B model with LoRA adapters
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Web Interface**: Streamlit frontend for easy interaction
- **Database Integration**: PostgreSQL for storing prediction history
- **Caching**: Redis caching for improved performance
- **Rate Limiting**: API rate limiting for resource protection
- **Async Processing**: Celery for asynchronous batch processing
- **Model Versioning**: MLflow for model tracking and versioning
- **Monitoring**: Prometheus metrics collection
- **Security**: Input validation and sanitization
- **Containerization**: Docker support for easy deployment
- **CI/CD**: GitHub Actions workflows for automated testing and deployment
- **Logging**: Comprehensive logging with file rotation

## Technology Stack

- **Backend**: FastAPI (Python 3.9)
- **Frontend**: Streamlit
- **Model Serving**: Hugging Face Transformers + PEFT
- **Database**: PostgreSQL
- **Caching**: Redis
- **Async Processing**: Celery + Redis
- **Model Versioning**: MLflow
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Project Structure

```
fine_tuning/
├── backend/              # FastAPI backend application
│   ├── app/              # Application source code
│   ├── tests/            # Unit tests
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend Docker configuration
├── frontend/             # Streamlit frontend application
│   ├── app.py            # Main Streamlit application
│   ├── requirements.txt  # Frontend dependencies
│   └── Dockerfile        # Frontend Docker configuration
├── model/                # Fine-tuned TinyLlama model
├── monitoring/           # Monitoring configurations
├── scripts/              # Utility scripts
├── .github/workflows/    # CI/CD workflows
├── docker-compose.yml    # Development environment configuration
├── docker-compose.prod.yml # Production environment configuration
└── project_plan.md       # Implementation plan
```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/v1/predict` - Single SMS spam prediction
- `POST /api/v1/predict/batch` - Batch spam detection
- `POST /api/v1/predict/batch/async` - Asynchronous batch processing
- `GET /api/v1/predict/batch/async/{job_id}` - Check async job status
- `GET /api/v1/history` - Retrieve prediction history
- `GET /metrics` - Prometheus metrics endpoint

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (recommended)
- Git

### Quick Start with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fine_tuning
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the services:
   - Streamlit Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000
   - MLflow: http://localhost:5000

### Manual Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

4. Run the backend:
   ```bash
   cd ../backend
   python app/main.py
   ```

5. In a new terminal, run the frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```

6. Start the Celery worker (for async processing):
   ```bash
   cd backend
   celery -A app.core.celery_app worker --loglevel=info
   ```

### Starting Services Individually

You can also start individual services using the provided scripts:

- Start main application: `scripts/start.bat` (Windows) or `scripts/start.sh` (Linux/Mac)
- Start Celery worker: `scripts/start_worker.bat` (Windows) or `scripts/start_worker.sh` (Linux/Mac)
- Start MLflow server: `scripts/start_mlflow.bat` (Windows) or `scripts/start_mlflow.sh` (Linux/Mac)

## Model Fine-Tuning Details

The TinyLlama-1.1B model was fine-tuned using advanced Parameter-Efficient Fine-Tuning (PEFT) techniques to achieve high accuracy while maintaining efficiency:

### Model Architecture
- **Base Model**: [TinyLlama/TinyLlama-1.1B-Chat-v1.0](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- **Task**: Sequence Classification for SMS Spam Detection
- **Labels**: 2 classes (spam/not_spam)
- **Training Dataset**: SMS Spam Collection dataset

### Fine-Tuning Methodology

#### QLoRA (Quantized LoRA)
The model was fine-tuned using QLoRA (Quantized Low-Rank Adaptation), which combines:
- **4-bit Quantization**: Reduces memory usage by quantizing the base model weights to 4-bit precision
- **Double Quantization**: Further compresses quantization constants to save additional memory
- **NormalFloat4 (NF4)**: Uses a specialized 4-bit quantization format optimized for normal distributions

#### LoRA Configuration
The LoRA adapters were configured with the following parameters:
- **Rank (r)**: 16 - Controls the dimensionality of the low-rank matrices
- **Alpha (lora_alpha)**: 32 - Scaling factor for the LoRA weights
- **Target Modules**: ["q_proj", "v_proj"] - Applies adapters to query and value projection layers in attention mechanisms
- **Dropout**: 0.05 - Regularization to prevent overfitting
- **Bias**: "none" - Does not train bias terms to save parameters
- **Modules to Save**: ["classifier", "score"] - Explicitly trains the classification head components

#### Training Configuration
- **Epochs**: 3 - Number of complete passes through the training dataset
- **Batch Size**: 16 per device with gradient accumulation steps of 2
- **Learning Rate**: 2e-4 - Optimized learning rate for stable training
- **Sequence Length**: 128 tokens - Maximum length for SMS text processing
- **Optimizer**: AdamW - Standard optimizer for transformer models
- **Loss Function**: Cross-entropy loss for binary classification

### Training Process
1. **Data Preparation**: 
   - Loaded SMS Spam Collection dataset
   - Split into 80% training / 20% testing
   - Tokenized using the base model's tokenizer with padding and truncation

2. **Model Preparation**:
   - Loaded base model with 4-bit quantization
   - Prepared model for k-bit training
   - Applied LoRA configuration with classification head training

3. **Training Execution**:
   - Used Hugging Face Transformers Trainer API
   - Monitored training metrics and validation accuracy
   - Saved PEFT adapters separately to preserve classification head weights

4. **Evaluation**:
   - Achieved 98% accuracy on test set
   - Trained only 0.22% of total model parameters (approximately 360K parameters)
   - Significantly reduced memory requirements compared to full fine-tuning

### Efficiency Benefits
- **Parameter Efficiency**: Trains only ~360K parameters instead of 1.1B+ parameters
- **Memory Efficiency**: 4-bit quantization reduces memory usage by ~75%
- **Storage Efficiency**: PEFT adapters are much smaller than full model weights
- **Inference Speed**: Maintains near-original inference speed
- **Deployment Flexibility**: Adapters can be easily applied to the base model

## Key Features Explained

### Redis Caching
The application uses Redis to cache prediction results, significantly improving response times for repeated queries.

### Rate Limiting
API endpoints are protected with rate limiting to prevent abuse:
- Single predictions: 10 requests/minute
- Batch predictions: 5 requests/minute
- Async batch submissions: 3 requests/minute
- History requests: 20 requests/minute

### Asynchronous Processing
Large batch jobs can be submitted for asynchronous processing using Celery, allowing the API to return immediately while processing continues in the background.

### Input Validation
All inputs are validated and sanitized to prevent SQL injection, XSS attacks, and other security issues.

### Model Versioning
MLflow integration allows for tracking model versions, parameters, and performance metrics.

## Monitoring

The application exposes Prometheus metrics at `/metrics` endpoint. Key metrics include:

- Request count by endpoint
- Request duration histograms
- System resource usage
- Prediction accuracy tracking

## Testing

Run the comprehensive feature test:
```bash
python test_features.py
```

Run unit tests:
```bash
cd backend
python -m pytest
```

## Deployment

For production deployment:

1. Update environment variables in docker-compose.prod.yml
2. Build and push Docker images to your registry
3. Deploy using your preferred orchestration platform

## Future Enhancements

- [x] Implement Redis caching for frequent predictions
- [x] Add rate limiting to API endpoints
- [x] Integrate Celery for asynchronous batch processing
- [x] Set up Grafana dashboards for visualization
- [x] Integrate MLflow for model versioning
- [x] Add authentication and authorization
- [x] Implement input validation and sanitization
- [ ] Add security headers and perform security audit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for educational purposes. Please check the licenses of the underlying models and datasets for commercial use.

## Acknowledgments

- [TinyLlama Model](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- [SMS Spam Collection Dataset](https://huggingface.co/datasets/sms_spam)