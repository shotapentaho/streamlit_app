import requests

url = "http://localhost:8080/pentaho/api/repos/:home:admin:SWheels_measures-PAZ.xanalyzer/viewer"
username = "admin"
password = "password"

response = requests.get(url, auth=(username, password))
print(response.headers)
print("Status Code:", response.status_code)
print("Response Text:", response.text[:500])  # Print first 500 characters of response