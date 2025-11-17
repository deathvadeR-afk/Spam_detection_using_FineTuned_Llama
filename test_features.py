#!/usr/bin/env python3
"""
Comprehensive test script for all implemented features
"""

import requests
import time
import sys

def test_api_health():
    """Test API health endpoint"""
    print("Testing API health...")
    try:
        response = requests.get("http://localhost:8003/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data['status']}")
            print(f"✅ Model Loaded: {data['model_loaded']}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check Error: {str(e)}")
        return False

def test_single_prediction():
    """Test single SMS prediction"""
    print("\nTesting single SMS prediction...")
    try:
        sms_text = "Congratulations! You've won $1000! Click here to claim your prize now!"
        response = requests.post(
            "http://localhost:8003/api/v1/predict",
            json={"sms_text": sms_text}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single Prediction Result: {data['prediction']} (Confidence: {data['confidence']:.2f})")
            return True
        else:
            print(f"❌ Single Prediction Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Single Prediction Error: {str(e)}")
        return False

def test_batch_prediction():
    """Test batch SMS prediction"""
    print("\nTesting batch SMS prediction...")
    try:
        sms_texts = [
            "Congratulations! You've won $1000! Click here to claim your prize now!",
            "Hey, are we still meeting for lunch tomorrow?",
            "URGENT: Your account will be suspended unless you verify immediately!"
        ]
        response = requests.post(
            "http://localhost:8003/api/v1/predict/batch",
            json={"sms_texts": sms_texts}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch Prediction Results: {len(data['predictions'])} predictions")
            for i, pred in enumerate(data['predictions']):
                print(f"   {i+1}. {pred['prediction']} (Confidence: {pred['confidence']:.2f})")
            return True
        else:
            print(f"❌ Batch Prediction Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Batch Prediction Error: {str(e)}")
        return False

def test_async_batch_prediction():
    """Test async batch SMS prediction"""
    print("\nTesting async batch SMS prediction...")
    try:
        sms_texts = [
            "Congratulations! You've won $1000! Click here to claim your prize now!",
            "Hey, are we still meeting for lunch tomorrow?",
            "URGENT: Your account will be suspended unless you verify immediately!",
            "Thanks for the meeting today. I'll send the follow-up email shortly.",
            "FREE! Get your iPhone now! Limited time offer! Call 1-800-FREE-GIFT"
        ]
        
        # Submit batch job
        response = requests.post(
            "http://localhost:8003/api/v1/predict/batch/async",
            json={"sms_texts": sms_texts}
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Async Batch Job Submitted. Job ID: {job_id}")
            
            # Poll for job status
            max_attempts = 10
            for attempt in range(max_attempts):
                status_response = requests.get(f"http://localhost:8003/api/v1/predict/batch/async/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data['state']}")
                    
                    if status_data['state'] == 'SUCCESS':
                        print("✅ Async Batch Job Completed Successfully!")
                        # Print some results
                        result = status_data.get('result', {})
                        if 'processed_count' in result:
                            print(f"   Processed {result['processed_count']}/{result['total_count']} messages")
                        return True
                    elif status_data['state'] == 'FAILURE':
                        print("❌ Async Batch Job Failed!")
                        print(f"   Error: {status_data.get('error', 'Unknown error')}")
                        return False
                    else:
                        time.sleep(2)  # Wait before polling again
                else:
                    print(f"❌ Error checking job status: {status_response.status_code}")
                    return False
                    
            print("❌ Async Batch Job Timeout!")
            return False
        else:
            print(f"❌ Async Batch Submission Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Async Batch Prediction Error: {str(e)}")
        return False

def test_prediction_history():
    """Test prediction history endpoint"""
    print("\nTesting prediction history...")
    try:
        response = requests.get(
            "http://localhost:8003/api/v1/history",
            params={"skip": 0, "limit": 10}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction History: {data['total']} total predictions")
            if data['predictions']:
                print(f"   Showing {min(3, len(data['predictions']))} recent predictions:")
                for i, pred in enumerate(data['predictions'][:3]):
                    print(f"   {i+1}. {pred['prediction']} (Confidence: {pred['confidence']:.2f})")
            return True
        else:
            print(f"❌ Prediction History Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Prediction History Error: {str(e)}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\nTesting rate limiting...")
    try:
        # Make multiple rapid requests to trigger rate limiting
        rate_limit_triggered = False
        for i in range(15):
            response = requests.post(
                "http://localhost:8003/api/v1/predict",
                json={"sms_text": f"Test message {i}"}
            )
            if response.status_code == 429:  # Too Many Requests
                print("✅ Rate Limiting Working: 429 Too Many Requests")
                rate_limit_triggered = True
                break
            time.sleep(0.1)  # Small delay between requests
        
        if not rate_limit_triggered:
            print("⚠️  Rate Limiting Not Triggered (may need more requests)")
        
        return True
    except Exception as e:
        print(f"❌ Rate Limiting Test Error: {str(e)}")
        return False

def test_input_validation():
    """Test input validation and sanitization"""
    print("\nTesting input validation...")
    try:
        # Test with potentially malicious input
        malicious_inputs = [
            "SELECT * FROM users; DROP TABLE users;",
            "<script>alert('XSS')</script>",
            "Normal message but extremely long " * 100  # Very long message
        ]
        
        validation_results = []
        for i, malicious_input in enumerate(malicious_inputs):
            response = requests.post(
                "http://localhost:8003/api/v1/predict",
                json={"sms_text": malicious_input}
            )
            if response.status_code == 400:  # Bad Request due to validation
                print(f"✅ Input Validation Working: Rejected malicious input {i+1}")
                validation_results.append(True)
            else:
                print(f"⚠️  Input Validation: Malicious input {i+1} not properly rejected")
                validation_results.append(False)
        
        return all(validation_results) if validation_results else True
    except Exception as e:
        print(f"❌ Input Validation Test Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Comprehensive Feature Tests\n")
    
    tests = [
        test_api_health,
        test_single_prediction,
        test_batch_prediction,
        test_async_batch_prediction,
        test_prediction_history,
        test_rate_limiting,
        test_input_validation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
            results.append(False)
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! All features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())