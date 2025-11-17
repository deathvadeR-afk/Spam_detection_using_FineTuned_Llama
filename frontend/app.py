import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Streamlit app configuration
st.set_page_config(
    page_title="TinyLlama SMS Spam Detector",
    page_icon="📱",
    layout="wide"
)

# API configuration
API_BASE_URL = "http://localhost:8003/api/v1"  # Local development
# API_BASE_URL = "http://backend:8003/api/v1"  # Docker environment

# Custom CSS for better UI
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-header {
        text-align: center;
        color: #333;
        padding: 1rem;
    }
    .result-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .spam {
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ffcdd2;
    }
    .ham {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #c8e6c9;
    }
    .prediction-history {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='main-header'>📱 TinyLlama SMS Spam Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Detect SMS spam using a fine-tuned TinyLlama model</p>", unsafe_allow_html=True)

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["🔍 Spam Detection", "📊 Prediction History", "⚡ Async Batch Processing"])

# Tab 1: Spam Detection
with tab1:
    st.header("Check if an SMS is spam")
    
    # Input area for SMS text
    sms_text = st.text_area(
        "Enter SMS message:",
        height=150,
        placeholder="Type or paste your SMS message here...",
        help="Enter the SMS message you want to check for spam"
    )
    
    # Prediction button
    if st.button("🔍 Check for Spam", type="primary", use_container_width=True):
        if not sms_text.strip():
            st.warning("Please enter an SMS message")
        else:
            with st.spinner("Analyzing message..."):
                try:
                    # Make API request
                    response = requests.post(
                        f"{API_BASE_URL}/predict",
                        json={"sms_text": sms_text},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display result
                        result_class = "spam" if data["prediction"] else "ham"
                        result_text = "SPAM" if data["prediction"] else "NOT SPAM"
                        confidence = data["confidence"] * 100
                        
                        st.markdown(
                            f"""
                            <div class="result-card {result_class}">
                                <h3>Result: {result_text}</h3>
                                <p><strong>Confidence:</strong> {confidence:.2f}%</p>
                                <p><strong>Message:</strong> {data['sms_text']}</p>
                                <p><strong>Timestamp:</strong> {data['timestamp']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend API. Please make sure the API is running.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Batch prediction section
    st.divider()
    st.header("Batch Spam Detection")
    
    batch_sms_texts = st.text_area(
        "Enter multiple SMS messages (one per line):",
        height=150,
        placeholder="Enter multiple SMS messages, each on a new line...",
        help="Enter multiple SMS messages for batch processing"
    )
    
    col1, col2 = st.columns(2)
    
    # Synchronous batch processing
    if col1.button("🔍 Check Batch for Spam", type="secondary", use_container_width=True):
        if not batch_sms_texts.strip():
            st.warning("Please enter SMS messages for batch processing")
        else:
            # Split the input into separate messages
            sms_list = [sms.strip() for sms in batch_sms_texts.split('\n') if sms.strip()]
            
            if not sms_list:
                st.warning("Please enter valid SMS messages")
            else:
                with st.spinner(f"Analyzing {len(sms_list)} messages..."):
                    try:
                        # Make batch API request
                        response = requests.post(
                            f"{API_BASE_URL}/predict/batch",
                            json={"sms_texts": sms_list},
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Display batch results
                            st.subheader(f"Batch Results ({len(data['predictions'])} messages)")
                            
                            # Create a dataframe for better visualization
                            results_data = []
                            for pred in data['predictions']:
                                results_data.append({
                                    "Message": pred["sms_text"][:50] + "..." if len(pred["sms_text"]) > 50 else pred["sms_text"],
                                    "Result": "SPAM" if pred["prediction"] else "NOT SPAM",
                                    "Confidence": f"{pred['confidence'] * 100:.2f}%"
                                })
                            
                            df = pd.DataFrame(results_data)
                            st.dataframe(df, use_container_width=True)
                            
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend API. Please make sure the API is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    # Asynchronous batch processing
    if col2.button("⚡ Check Batch Async", type="secondary", use_container_width=True):
        if not batch_sms_texts.strip():
            st.warning("Please enter SMS messages for batch processing")
        else:
            # Split the input into separate messages
            sms_list = [sms.strip() for sms in batch_sms_texts.split('\n') if sms.strip()]
            
            if not sms_list:
                st.warning("Please enter valid SMS messages")
            else:
                with st.spinner(f"Submitting {len(sms_list)} messages for async processing..."):
                    try:
                        # Make async batch API request
                        response = requests.post(
                            f"{API_BASE_URL}/predict/batch/async",
                            json={"sms_texts": sms_list},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            job_id = data["job_id"]
                            
                            st.success(f"Batch job submitted successfully! Job ID: {job_id}")
                            
                            # Show job status tracking
                            status_placeholder = st.empty()
                            result_placeholder = st.empty()
                            
                            # Poll for job status
                            while True:
                                status_response = requests.get(f"{API_BASE_URL}/predict/batch/async/{job_id}", timeout=10)
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    status_placeholder.info(f"Job Status: {status_data['state']}")
                                    
                                    if status_data['state'] == 'SUCCESS':
                                        status_placeholder.success("Job completed successfully!")
                                        result_placeholder.json(status_data['result'])
                                        break
                                    elif status_data['state'] == 'FAILURE':
                                        status_placeholder.error("Job failed!")
                                        result_placeholder.error(status_data.get('error', 'Unknown error'))
                                        break
                                    else:
                                        time.sleep(2)  # Wait before polling again
                                else:
                                    status_placeholder.error(f"Error checking job status: {status_response.status_code}")
                                    break
                                    
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend API. Please make sure the API is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

# Tab 2: Prediction History
with tab2:
    st.header("Prediction History")
    
    # Load history button
    if st.button("📊 Load Prediction History", type="primary", use_container_width=True):
        with st.spinner("Loading prediction history..."):
            try:
                # Make API request to get predictions
                response = requests.get(
                    f"{API_BASE_URL}/history",
                    params={"skip": 0, "limit": 50},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["predictions"]:
                        st.subheader(f"Recent Predictions ({data['total']} total)")
                        
                        # Create a dataframe for better visualization
                        history_data = []
                        for pred in data["predictions"]:
                            history_data.append({
                                "Message": pred["sms_text"][:50] + "..." if len(pred["sms_text"]) > 50 else pred["sms_text"],
                                "Result": "SPAM" if pred["prediction"] else "NOT SPAM",
                                "Confidence": f"{pred['confidence'] * 100:.2f}%",
                                "Timestamp": pred["timestamp"]
                            })
                        
                        df = pd.DataFrame(history_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Show a chart of spam vs ham distribution
                        spam_count = sum(1 for pred in data["predictions"] if pred["prediction"])
                        ham_count = len(data["predictions"]) - spam_count
                        
                        st.subheader("Spam vs Ham Distribution")
                        chart_data = pd.DataFrame({
                            "Type": ["SPAM", "NOT SPAM"],
                            "Count": [spam_count, ham_count]
                        })
                        st.bar_chart(chart_data.set_index("Type"))
                    else:
                        st.info("No prediction history found")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend API. Please make sure the API is running.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Tab 3: Async Batch Processing
with tab3:
    st.header("Async Batch Processing")
    st.markdown("""
    Submit large batches of SMS messages for asynchronous processing. 
    This is ideal for processing hundreds or thousands of messages without blocking the interface.
    """)
    
    st.subheader("Upload SMS File")
    uploaded_file = st.file_uploader("Choose a text file with SMS messages (one per line)", type="txt")
    
    if uploaded_file is not None:
        # Read file content
        stringio = uploaded_file.getvalue().decode("utf-8")
        sms_list = [line.strip() for line in stringio.split('\n') if line.strip()]
        
        st.info(f"Loaded {len(sms_list)} SMS messages from file")
        
        if st.button("🚀 Process File Async", type="primary", use_container_width=True):
            with st.spinner(f"Submitting {len(sms_list)} messages for async processing..."):
                try:
                    # Make async batch API request
                    response = requests.post(
                        f"{API_BASE_URL}/predict/batch/async",
                        json={"sms_texts": sms_list},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_id = data["job_id"]
                        
                        st.success(f"Batch job submitted successfully! Job ID: {job_id}")
                        
                        # Show job status tracking
                        status_placeholder = st.empty()
                        result_placeholder = st.empty()
                        
                        # Poll for job status
                        while True:
                            status_response = requests.get(f"{API_BASE_URL}/predict/batch/async/{job_id}", timeout=10)
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status_placeholder.info(f"Job Status: {status_data['state']}")
                                
                                if status_data['state'] == 'SUCCESS':
                                    status_placeholder.success("Job completed successfully!")
                                    result_placeholder.json(status_data['result'])
                                    break
                                elif status_data['state'] == 'FAILURE':
                                    status_placeholder.error("Job failed!")
                                    result_placeholder.error(status_data.get('error', 'Unknown error'))
                                    break
                                else:
                                    time.sleep(2)  # Wait before polling again
                            else:
                                status_placeholder.error(f"Error checking job status: {status_response.status_code}")
                                break
                                
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend API. Please make sure the API is running.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    st.divider()
    st.subheader("Manual Entry")
    manual_sms_texts = st.text_area(
        "Enter SMS messages for async processing (one per line):",
        height=200,
        placeholder="Enter multiple SMS messages, each on a new line...",
        help="These will be processed asynchronously in the background"
    )
    
    if st.button("🚀 Process Manual Entries Async", type="secondary", use_container_width=True):
        if not manual_sms_texts.strip():
            st.warning("Please enter SMS messages for processing")
        else:
            # Split the input into separate messages
            sms_list = [sms.strip() for sms in manual_sms_texts.split('\n') if sms.strip()]
            
            if not sms_list:
                st.warning("Please enter valid SMS messages")
            else:
                with st.spinner(f"Submitting {len(sms_list)} messages for async processing..."):
                    try:
                        # Make async batch API request
                        response = requests.post(
                            f"{API_BASE_URL}/predict/batch/async",
                            json={"sms_texts": sms_list},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            job_id = data["job_id"]
                            
                            st.success(f"Batch job submitted successfully! Job ID: {job_id}")
                            
                            # Show job status tracking
                            status_placeholder = st.empty()
                            result_placeholder = st.empty()
                            
                            # Poll for job status
                            while True:
                                status_response = requests.get(f"{API_BASE_URL}/predict/batch/async/{job_id}", timeout=10)
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    status_placeholder.info(f"Job Status: {status_data['state']}")
                                    
                                    if status_data['state'] == 'SUCCESS':
                                        status_placeholder.success("Job completed successfully!")
                                        result_placeholder.json(status_data['result'])
                                        break
                                    elif status_data['state'] == 'FAILURE':
                                        status_placeholder.error("Job failed!")
                                        result_placeholder.error(status_data.get('error', 'Unknown error'))
                                        break
                                    else:
                                        time.sleep(2)  # Wait before polling again
                                else:
                                    status_placeholder.error(f"Error checking job status: {status_response.status_code}")
                                    break
                                    
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend API. Please make sure the API is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

# Sidebar with information
st.sidebar.title("About")
st.sidebar.info("""
This application uses a fine-tuned TinyLlama-1.1B model with PEFT (LoRA) techniques for SMS spam detection.

**Key Features:**
- 98% test accuracy
- Parameter-efficient fine-tuning
- Real-time spam detection
- Batch processing capability
- Asynchronous batch processing
- Prediction history tracking
""")

st.sidebar.title("Model Information")
st.sidebar.info("""
**Base Model:** TinyLlama/TinyLlama-1.1B-Chat-v1.0
**Fine-tuning Method:** LoRA with 4-bit quantization
**Training Data:** SMS Spam Collection dataset
**Performance:** 98% accuracy on test set
**Efficiency:** Trains only 0.22% of model parameters
""")

st.sidebar.title("Tech Stack")
st.sidebar.info("""
- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit
- **Model Serving:** Hugging Face Transformers + PEFT
- **Database:** PostgreSQL
- **Caching:** Redis
- **Async Processing:** Celery + Redis
- **Monitoring:** Prometheus + Grafana
""")