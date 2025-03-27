import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Streamlit UI
st.title("📊 Pentaho Analyzer (PAZ) by Folder breakdown")

# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")

# Default report path (Modify this based on your Pentaho setup)
#report_path = "/pentaho/api/repos/%3Ahome%3Aadmin%3ASWheels_measures-PAZ.xanalyzer/viewer"
#report_path = "/pentaho/api/repos/:home:admin:SWheels_measures-PAZ.xanalyzer/viewer"
#report_path = "/pentaho/api/repos/:public:Steel%20Wheels:Product%20Line%20By%20Quantity(Funnel).xanalyzer/viewer"
sw_directory_path="pentaho/api/repos/:public:"
report_path = "/pentaho/api/repo/files/:public"
#schema_path  = "/pentaho/api/repos/xanalyzer/service/selectSchema"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the Analyzer Report
#server_url = "http://"+username+":"+password+"@"+server_url
def fetch_analyzer_report(server_url):
        full_url = server_url + report_path +"/children" # Construct full API URL
        
        try:           
            response = requests.get(full_url, auth=(username, password))
            # Check if response is successful
            if response.status_code == 200:
                # Parse XML
                root = ET.fromstring(response.text)
                
                #Extract folder names and reports in one loop
                folders = []                
                for item in root.findall("repositoryFileDto"):
                    file_type = item.find("folder").text  # Check if it's a folder
                    file_name = item.find("name").text  # Get the name
                   
                    if file_type == "true":  # If it's a folder
                        folders.append(file_name)  # Store the folder name                   
                
                #Display folders📂
                for folder in folders:
                    st.write(f"📂 {folder}")  # Print the folder name
                    full_url = server_url + report_path + ":"+urllib.parse.quote(folder)+"/children" # Construct full API URL
                    #st.write(full_url)  # Print the folder name
                    response_folder_level = requests.get(full_url, auth=(username, password))
                    # Check if response is successful
                    if response_folder_level.status_code == 200:
                        analyzer_reports = []
                        # Parse XML
                        root = ET.fromstring(response_folder_level.text)
                        for item in root.findall("repositoryFileDto"):
                            file_name = item.find("name").text  # Get the name
                            if file_name.endswith(".xanalyzer"):
                                analyzer_reports.append(file_name)  # Store report name
                   
                    st.success("✅ Report Links are: ")
                    for report in analyzer_reports:
                        st_full_url = f"{server_url}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(report)}/viewer"
                        st.write(f"📊 {st_full_url}")
                        #st.write("🔹 Analyzer Reports:", len(analyzer_reports))  
                        
                else:
                    st.write("No Analyzer reports found.")
                    
            else:
                st.success("❌ Request failed with status:", response.status_code, response.text)
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
            #st.write(f"- {report_data}")
            st.success("✅ Report Links Generated Successfully!")
            #Assuming the report is a PDF, provide a download option
            #st.download_button(
             #   label="📥 Download Report",
             #   data=report_data,
              #  file_name="European Sales (geo map).pdf",
              #  mime="application/pdf"
            #)
    else:
        st.warning("⚠ Please enter a valid Pentaho Server URL.")
