import requests
import json

# Test the health endpoint
print("Testing health endpoint...")
response = requests.get("http://localhost:8003/health")
print(f"Health check: {response.status_code} - {response.json()}")

# Test the prediction endpoint
print("\nTesting prediction endpoint...")
test_data = {
    "sms_text": "Congratulations! You've won a $1000 gift card. Click here to claim now!"
}

response = requests.post(
    "http://localhost:8003/api/v1/predict",
    headers={"Content-Type": "application/json"},
    data=json.dumps(test_data)
)

if response.status_code == 200:
    result = response.json()
    print(f"Prediction result: {result}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test another message
print("\nTesting another message...")
test_data2 = {
    "sms_text": "Hey, are we still meeting for lunch today?"
}

response2 = requests.post(
    "http://localhost:8003/api/v1/predict",
    headers={"Content-Type": "application/json"},
    data=json.dumps(test_data2)
)

if response2.status_code == 200:
    result2 = response2.json()
    print(f"Prediction result: {result2}")
else:
    print(f"Error: {response2.status_code} - {response2.text}")