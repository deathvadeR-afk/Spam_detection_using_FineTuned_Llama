#!/usr/bin/env python3
"""
Test script for async batch processing functionality
"""

import requests
import time
import sys

def test_async_batch_processing():
    """Test async batch processing"""
    base_url = "http://localhost:8000/api/v1"
    
    # Sample SMS texts
    sms_texts = [
        "Congratulations! You've won $1000! Click here to claim your prize now!",
        "Hey, are we still meeting for lunch tomorrow?",
        "URGENT: Your account will be suspended unless you verify immediately!",
        "Thanks for the meeting today. I'll send the follow-up email shortly.",
        "FREE! Get your iPhone now! Limited time offer! Call 1-800-FREE-GIFT"
    ]
    
    print("Testing async batch processing...")
    
    # Submit batch job
    batch_data = {"sms_texts": sms_texts}
    response = requests.post(f"{base_url}/predict/batch/async", json=batch_data)
    
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"Batch job submitted successfully. Job ID: {job_id}")
        
        # Poll for job status
        while True:
            status_response = requests.get(f"{base_url}/predict/batch/async/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Job status: {status_data['state']}")
                
                if status_data['state'] == 'SUCCESS':
                    print("Job completed successfully!")
                    print(f"Results: {status_data['result']}")
                    break
                elif status_data['state'] == 'FAILURE':
                    print("Job failed!")
                    print(f"Error: {status_data.get('error', 'Unknown error')}")
                    break
                else:
                    print("Job still processing...")
                    time.sleep(2)  # Wait 2 seconds before polling again
            else:
                print(f"Error checking job status: {status_response.status_code}")
                print(status_response.text)
                break
    else:
        print(f"Error submitting batch job: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_async_batch_processing()