import httpx
import time

url = "http://localhost:8000/api/upload-kml"

try:
    with open('Backend/test.kml', 'rb') as f:
        files = {'file': f}
        data = {
            'site_name': 'Test GEE Site',
            'activities_json': '["Crop production"]'
        }
        print("Uploading test.kml to TNFD backend...")
        response = httpx.post(url, files=files, data=data, timeout=30.0)
        print(f"Upload Status Code: {response.status_code}")
        print(f"Upload Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
