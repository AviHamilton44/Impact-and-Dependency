import httpx

url = "http://localhost:8000/api/upload-kml"

files = {'file': open('C:\\Users\\Admin\\OneDrive\\Desktop\\Current desktop file\\Sarath.kml', 'rb')}
data = {
    'site_name': 'Test Sarath KML',
    'activities_json': '["Agricultural Products"]'
}

response = httpx.post(url, files=files, data=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
