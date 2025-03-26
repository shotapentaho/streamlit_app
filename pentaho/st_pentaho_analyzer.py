import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Streamlit UI
st.title("📊 Pentaho Analyzer in Streamlit")

st.write((requests.__version__))


import subprocess

curl_command = [
    "curl",
    "-u", "admin:password",
    "http://127.0.0.1:8080/pentaho/api/repo/files/:public:Steel%20Wheels/children"
]

result = subprocess.run(curl_command, capture_output=True, text=True)
st.write(result.stdout)


# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")
# Default report path (Modify this based on your Pentaho setup)
#report_path = "/pentaho/api/repos/%3Ahome%3Aadmin%3ASWheels_measures-PAZ.xanalyzer/viewer"
#report_path = "/pentaho/api/repos/:home:admin:SWheels_measures-PAZ.xanalyzer/viewer"
#report_path = "/pentaho/api/repos/:public:Steel%20Wheels:Product%20Line%20By%20Quantity(Funnel).xanalyzer/viewer"
report_path = "/pentaho/api/repo/files/:public:Steel%20Wheels/children"
#schema_path  = "/pentaho/api/repos/xanalyzer/service/selectSchema"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the Analyzer Report
#server_url = "http://"+username+":"+password+"@"+server_url
def fetch_analyzer_report(server_url):
        full_url = server_url + report_path  # Construct full API URL
        
        try:           
            response = requests.get("http://localhost:8080/pentaho/api/repo/files/:public:Steel%20Wheels/children", auth=(username, password), verify=False, timeout=10)
            st.success(response.status_code)
            # Check if response is successful
            if response.status_code == 200:
                st.success(response.status_code)
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

           
            #st.success("Status Code:", response.status_code)
            response.raise_for_status()  # Check for errors
            return response.content  # Report content (PDF, XML, JSON)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching report: {e}")
            return None

if st.button("Run Report"):
    if pentaho_server:
        report_data = fetch_analyzer_report(pentaho_server)
        if report_data:
            st.success("✅ Report Generated Successfully!")

            # Assuming the report is a PDF, provide a download option
            st.download_button(
                label="📥 Download Report",
                data=report_data,
                file_name="SWheels_measures-PAZ.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠ Please enter a valid Pentaho Server URL.")
