import streamlit as st
import requests

# Streamlit UI
st.title("📊 Pentaho Analyzer in Streamlit")
# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")
# Default report path (Modify this based on your Pentaho setup)
#report_path = "/pentaho/api/repos/%3Ahome%3Aadmin%3ASWheels_measures-PAZ.xanalyzer/viewer"
#report_path = "/pentaho/api/repos/:home:admin:SWheels_measures-PAZ.xanalyzer/viewer"
report_path = "/pentaho/api/repos/:public:Steel Wheels:Product Line By Quantity(Funnel).xanalyzer/viewer"
#schema_path  = "/pentaho/api/repos/xanalyzer/service/selectSchema"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the Analyzer Report
#server_url = "http://"+username+":"+password+"@"+server_url
def fetch_analyzer_report(server_url):
        full_url = server_url + report_path  # Construct full API URL
        proxies = {"http": None, "https": None}
   
        try:
            st.success(full_url)
            response = requests.get(full_url, auth=(username, password), proxies=proxies)
            st.success("Status Code:", response.status_code)
            st.success(response)
            response.raise_for_status()  # Check for errors
            return response.content  # Report content (PDF, XML, JSON)
        except requests.exceptions.RequestException as e:
            #st.error(f"Error fetching report: {e}")
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
