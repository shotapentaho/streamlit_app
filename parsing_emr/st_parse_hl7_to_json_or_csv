import streamlit as st
from hl7apy.parser import parse_message
import pandas as pd
import json

st.set_page_config(page_title="HL7 to JSON/CSV", layout="wide")

st.title("📄 HL7 File Parser")
uploaded_file = st.file_uploader("Upload an HL7 message file", type=["hl7", "txt"])

if uploaded_file:
    raw_hl7 = uploaded_file.read().decode("utf-8").strip()
    
    try:
        message = parse_message(raw_hl7)
        st.success("HL7 message parsed successfully!")

        # Extract data from segments
        pid = message.segment("PID")
        patient_info = {
            "Patient ID": pid.patient_identifier_list[0].cx_1.value,
            "Last Name": pid.patient_name[0].family_name.fn_1.value,
            "First Name": pid.patient_name[0].given_name.value,
            "DOB": pid.date_time_of_birth.value,
            "Gender": pid.administrative_sex.value
        }

        st.subheader("👤 Patient Info")
        st.json(patient_info)

        # Extract all OBX segments
        obx_data = []
        for obx in message.children:
            if obx.name == "OBX":
                obx_data.append({
                    "Observation ID": obx.observation_identifier.ce_1.value,
                    "Observation Desc": obx.observation_identifier.ce_2.value,
                    "Value": obx.observation_value[0].value,
                    "Units": obx.units.ce_1.value if obx.units else "",
                })

        if obx_data:
            st.subheader("🧪 Observations")
            df = pd.DataFrame(obx_data)
            st.dataframe(df)

            # CSV download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "observations.csv", "text/csv")

            # JSON download
            json_data = json.dumps(obx_data, indent=2)
            st.download_button("Download JSON", json_data, "observations.json", "application/json")

    except Exception as e:
        st.error(f"Error parsing HL7 message: {str(e)}")
