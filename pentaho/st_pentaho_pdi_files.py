import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Streamlit UI for Pentaho ETL
st.set_page_config(page_title="Pentaho ETL (Jobs and Transformations) ", layout="wide")
st.title("📊 Pentaho Jobs and Transformations by folders..")

# User Input for Pentaho Server
pentaho_server = st.text_input("Enter Pentaho Server & Port", "http://localhost:8080")

# Default report path (Modify this based on your Pentaho setup)
sw_directory_path = "pentaho/api/repos/:public:"
ktr_kjb_path = "/pentaho/api/repo/files/:public"

# Pentaho Authentication
username = "admin"
password = "password"

# Function to fetch the Pentaho reports
def fetch_pdi_objects(server_url, type_of_etl):
    full_url = server_url + ktr_kjb_path + "/children"  # Construct full API URL

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
                    full_url = server_url + ktr_kjb_path + ":" + urllib.parse.quote(folder) + "/children"
                    response_folder_level = requests.get(full_url, auth=(username, password))
                    
                    if response_folder_level.status_code == 200:
                        pentaho_etl = []
                        root = ET.fromstring(response_folder_level.text)
                        for item in root.findall("repositoryFileDto"):
                            file_name = item.find("name").text
                            if file_name.endswith(type_of_etl):
                                pentaho_etl.append(file_name)  # Add a job or transformation

                        # Display the folder with the count of reports
                        artefact_count = len(pentaho_etl)
                        with st.expander(f"📂 {folder} + ({artefact_count} {type_of_etl} ETL objects)"):
                            if pentaho_etl:
                                for etl_artefact in pentaho_etl:
                                    # Construct the viewer URL for each ktr/kjb
                                    if type_of_etl == ".kjb":
                                        etl_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(etl_artefact)}/viewer"
                                        st.write(f"🔗 [**{etl_artefact}**]({etl_url})")
                                    elif type_of_etl == ".ktr":
                                        etl_url = f"{pentaho_server}/{sw_directory_path}{urllib.parse.quote(folder)}:{urllib.parse.quote(etl_artefact)}/viewer"
                                        st.write(f"🔗 [**{etl_artefact}**]({etl_url})")                                    
                            else:
                                st.warning("⚠️ No reports found in this folder.")
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

# List of available options (Drop Down)
options = ["Job", "Transformation"]
selected_option = st.selectbox("Choose PDI type to list by folder:", options)
type_of_etl=''

# Perform action based on selection
if selected_option == "Job":
    type_of_etl='.kjb'
    fetch_pdi_objects(pentaho_server, type_of_etl)  # Jobs 
elif selected_option == "Transformation":
    type_of_etl='.ktr'
    fetch_pdi_objects(pentaho_server, type_of_etl)   # Transformations
