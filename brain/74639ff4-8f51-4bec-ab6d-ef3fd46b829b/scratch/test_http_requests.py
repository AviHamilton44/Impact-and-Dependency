import requests

baseURL = 'http://localhost:8000/api'

# 1. Fetch sites first
resp = requests.get(f"{baseURL}/sites")
sites = resp.json()
print(f"Current sites count: {len(sites)}")

if len(sites) > 0:
    target_id = sites[0]["site_id"]
    print(f"Attempting to delete site {target_id}...")
    del_resp = requests.delete(f"{baseURL}/sites/{target_id}")
    print(f"Delete Response Status: {del_resp.status_code}")
    print(f"Delete Response Body: {del_resp.text}")
    
# 2. Test clear all
print("Attempting to clear all sites...")
clear_resp = requests.post(f"{baseURL}/sites/clear")
print(f"Clear Response Status: {clear_resp.status_code}")
print(f"Clear Response Body: {clear_resp.text}")

# 3. Check count again
resp = requests.get(f"{baseURL}/sites")
sites = resp.json()
print(f"Post-clear sites count: {len(sites)}")
