import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Streamlit UI for Pentaho Reporting
st.set_page_config(page_title="Pentaho Reports Listing", layout="wide")
st.title("📊 Pentaho Reports (PAZ, PRD, PIR) by Folders")

# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080/")

# Base Pentaho API Paths
reports_directory_path = "pentaho/api/repos"
base_path = "pentaho/api/repo/files"
repo_path = f"{base_path}/:public"

# Pentaho Authentication
username = "admin"
password = "password"

# Recursive function to fetch reports from all folders and subfolders
def fetch_reports_recursively(server_url, current_path, type_report, indent=0):
    try:
        full_url = server_url + current_path + "/children"
        response = requests.get(full_url, auth=(username, password))

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            folders = []
            reports = []

            # Separate folders and reports
            for item in root.findall("repositoryFileDto"):
                file_name = item.find("name").text
                is_folder = item.find("folder").text == "true"

                if is_folder:
                    folders.append(file_name)
                elif file_name.endswith(type_report):
                    reports.append(file_name)

            # Sort Folders and Reports Alphabetically
            folders.sort()
            reports.sort()

            # Get Parent Folder Name
            folder_name = current_path.strip('/').split(':')[-1] or "Root"

            # Display Parent Folder First
            folder_report_count = len(reports)
            # Display Parent Folder First with Indentation
            folder_label = f"{'→ ' * indent}📂 {folder_name} ({len(reports)} {type_report} reports)"

            with st.expander(folder_label):                
                # Display Reports inside the parent folder first
                for report in reports:
                    if type_report in [".xanalyzer", ".prpt"]:
                        report_url = f"{server_url}/{urllib.parse.quote(current_path)}:{urllib.parse.quote(report)}/viewer"
                    elif type_report == ".prpti":
                        report_url = f"{server_url}/{urllib.parse.quote(current_path)}:{urllib.parse.quote(report)}/prpti.view"

                    report_url = report_url.replace("//pentaho", "/pentaho").replace(base_path, reports_directory_path)
                    st.write(f"🔗 [**{report}**]({report_url})")

            # After showing the parent folder and its reports, go inside each subfolder
            for folder in folders:
                new_path = f"{current_path}:{folder}"
                fetch_reports_recursively(server_url, new_path, type_report, indent + 1)

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")

# Dropdown for selecting report type
options = {
    "PAZ - Pentaho Analyzer Report": ".xanalyzer",
    "PRD - Pentaho Report Designer": ".prpt",
    "PIR - Pentaho Interactive Reporting": ".prpti"
}
selected_option = st.selectbox("Select report type:", list(options.keys()))

# Fetch reports when user selects an option
if selected_option and pentaho_server:
    type_report = options[selected_option]
    fetch_reports_recursively(pentaho_server, repo_path, type_report)
