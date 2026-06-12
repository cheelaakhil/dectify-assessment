import requests
import json

url = "https://dectify-assessment.vercel.app/api/auth/signup"
data = {
    "name": "traceback_test2",
    "email": "traceback2@test.com",
    "password": "test"
}

try:
    response = requests.post(url, json=data)
    with open("traceback_out.json", "w") as f:
        json.dump(response.json(), f, indent=2)
except Exception as e:
    print("Request failed:", e)
