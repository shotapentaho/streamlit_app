import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Streamlit UI
st.set_page_config(page_title="Pentaho Analyzer (PAZ) Reports", layout="wide")
st.title("📊 Pentaho Analyzer (PAZ) by folders..")

# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")

# Default report path (Modify this based on your Pentaho setup)
sw_directory_path = "pentaho/api/repos/:public:"
report_path = "/pentaho/api/repo/files/:public"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the analyzer reports
def fetch_analyzer_report(server_url):
    full_url = server_url + report_path + "/children"  # Construct full API URL

    try:
        response = requests.get(full_url, auth=(username, password))
        if response.status_code == 200:
            # Parse XML response to extract folders
            root = ET.fromstring(response.text)
            folders = []
            for item in root.findall("repositoryFileDto"):
                file_type = item.find("folder").text  # Check if it's a folder
                file_name = item.find("name").text  # Get the name
                if file_type == "true":  # If it's a folder
                    folders.append(file_name)  # Add folder name to the list

            # Display folders as collapsible sections
            if folders:
                for folder in folders:
                    # Construct API URL to fetch reports within the selected folder
                    full_url = server_url + report_path + ":" + urllib.parse.quote(folder) + "/children"
                    response_folder_level = requests.get(full_url, auth=(username, password))

                    if response_folder_level.status_code == 200:
                        analyzer_reports = []
                        root = ET.fromstring(response_folder_level.text)
                        for item in root.findall("repositoryFileDto"):
                            file_name = item.find("name").text
                            if file_name.endswith(".xanalyzer"):
                                analyzer_reports.append(file_name)  # Add analyzer report

                        # Display the folder with the count of reports
                        folder_report_count = len(analyzer_reports)
                        with st.expander(f"📂 {folder} + ({folder_report_count} PAZ reports)"):
                            if analyzer_reports:
                                for report in analyzer_reports:
                                    # Construct the viewer URL for each report
                                    report_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(report)}/viewer"
                                    st.write(f"🔗 [**{report}**]({report_url})")
                            else:
                                st.warning("⚠️ No Analyzer reports found in this folder.")
                    else:
                        st.error(f"❌ Error fetching reports for folder {folder}: {response_folder_level.status_code}")
            else:
                st.warning("⚠️ No folders found in the repository.")
        else:
            st.error(f"❌ Error fetching folders: {response.status_code}")
        response.raise_for_status()  # Check for errors
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
    return None

# Trigger the report fetching process when the button is clicked
if st.button("Fetch PAZ Links by Folder"):
    if pentaho_server:
        fetch_analyzer_report(pentaho_server)
    else:
        st.warning("⚠️ Please enter a valid Pentaho Server URL.")
