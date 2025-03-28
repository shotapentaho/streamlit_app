import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Streamlit UI
st.set_page_config(page_title="Pentaho Reports (PAZ, PRD, PIR) ", layout="wide")
st.title("📊 Pentaho Reports by folders..")

# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")

# Default report path (Modify this based on your Pentaho setup)
sw_directory_path = "pentaho/api/repos/:public:"
report_path = "/pentaho/api/repo/files/:public"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the analyzer reports
def fetch_pentaho_report(server_url, type_report):
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
                        pentaho_reports = []
                        root = ET.fromstring(response_folder_level.text)
                        for item in root.findall("repositoryFileDto"):
                            file_name = item.find("name").text
                            if file_name.endswith(type_report):
                                pentaho_reports.append(file_name)  # Add analyzer report

                        # Display the folder with the count of reports
                        folder_report_count = len(pentaho_reports)
                        with st.expander(f"📂 {folder} + ({folder_report_count} {type_report} reports)"):
                            if pentaho_reports:
                                for report in pentaho_reports:
                                    # Construct the viewer URL for each report
                                    if type_report == ".xanalyzer":
                                        report_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(report)}/viewer"
                                        st.write(f"🔗 [**{report}**]({report_url})")
                                    elif type_report == ".prpt":
                                        report_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(report)}/viewer"
                                        st.write(f"🔗 [**{report}**]({report_url})")
                                    elif type_report == ".prpti":
                                        report_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(report)}/prpti.view"
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
#if st.button("Fetch PAZ by Folder"):
#    if pentaho_server:
#        fetch_analyzer_report(pentaho_server)
#    else:
#        st.warning("⚠️ Please enter a valid Pentaho Server URL.")

# Function to fetch the PRD reports
def fetch_prd_report(server_url):
    st.write("⚠️ Yet to have tje code for PRPT ")


# Function to fetch the PRD reports
def fetch_pir_report(server_url):
    st.write("⚠️ Yet to have code for PIR ")


# List of available options
options = ["PRD", "PAZ", "PIR"]
# Create a dropdown (selectbox) instead of a button
selected_option = st.selectbox("Choose report type to list by folder:", options)
type_report=''

# Perform action based on selection
if selected_option == "PRD":
    type_report='.prpt'
    fetch_pentaho_report(pentaho_server, type_report)  # Call function for PRD reports
elif selected_option == "PAZ":
    type_report='.xanalyzer'
    fetch_pentaho_report(pentaho_server, type_report)   # Call function for PAZ reports
elif selected_option == "PIR":
    type_report='.prpti'
    fetch_pentaho_report(pentaho_server, type_report)   # Call function for other reports