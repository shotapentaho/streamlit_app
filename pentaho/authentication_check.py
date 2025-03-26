import requests
import xml.etree.ElementTree as ET

url = "http://localhost:8080/pentaho/api/repo/files/:public:Steel%20Wheels/children"
username = "admin"
password = "password"

response = requests.get(url, auth=(username, password))
#print(response.headers)
print("Status Code:", response.status_code)
#print(response.text)
#print("Response Text:", response.text[:500])  # Print first 500 characters of response


# Check if response is successful
if response.status_code == 200:
    # Parse XML
    root = ET.fromstring(response.text)
    # Extract report names
    analyzer_reports = [
        file.find("name").text
        for file in root.findall("repositoryFileDto")
        if file.find("name").text.endswith(".xanalyzer")
    ]
    print(len(analyzer_reports))
    print("🔹 Analyzer Reports:", len(analyzer_reports))
    for report in analyzer_reports:
        print(f"- {report}")

else:
    print("❌ Request failed with status:", response.status_code, response.text)
