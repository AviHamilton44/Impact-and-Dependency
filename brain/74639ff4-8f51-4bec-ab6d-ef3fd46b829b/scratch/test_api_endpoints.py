import urllib.request
import urllib.error
import json

def make_request(url, method="GET"):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

# 1. Fetch sites
status, body = make_request("http://127.0.0.1:8000/api/sites")
print(f"Fetch sites status: {status}")
if status == 200:
    sites = json.loads(body)
    print(f"Returned {len(sites)} sites.")
    if sites:
        site_id = sites[0]["site_id"]
        print(f"Attempting to delete site {site_id} via API...")
        del_status, del_body = make_request(f"http://127.0.0.1:8000/api/sites/{site_id}", method="DELETE")
        print(f"Delete response status: {del_status}, body: {del_body}")
        
print("Attempting to clear all sites via API...")
clear_status, clear_body = make_request("http://127.0.0.1:8000/api/sites/clear", method="POST")
print(f"Clear response status: {clear_status}, body: {clear_body}")
