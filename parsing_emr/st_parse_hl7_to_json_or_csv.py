import streamlit as st
import pandas as pd
import json

def parse_hl7_to_segments(raw):
    segments = raw.strip().split("\n")
    return [line.strip().split("|") for line in segments if line.strip()]

def extract_data(segments):
    patient_info = {}
    observations = []

    for segment in segments:
        seg_type = segment[0]

        if seg_type == "PID":
            patient_info = {
                "Patient ID": segment[3] if len(segment) > 3 else "",
                "Last Name": segment[5].split("^")[0] if len(segment) > 5 else "",
                "First Name": segment[5].split("^")[1] if len(segment) > 5 and "^" in segment[5] else "",
                "DOB": segment[7] if len(segment) > 7 else "",
                "Gender": segment[8] if len(segment) > 8 else ""
            }

        elif seg_type == "OBX":
            obs = {
                "Observation ID": segment[3].split("^")[0] if len(segment) > 3 else "",
                "Observation Desc": segment[3].split("^")[1] if len(segment) > 3 and "^" in segment[3] else "",
                "Value": segment[5] if len(segment) > 5 else "",
                "Units": segment[6] if len(segment) > 6 else ""
            }
            observations.append(obs)

    return patient_info, observations

st.title("📄 HL7 Parser (Simple + Robust)")

uploaded_file = st.file_uploader("Upload your HL7 file", type=["hl7", "txt"])
if uploaded_file:
    hl7_data = uploaded_file.read().decode("utf-8")
    segments = parse_hl7_to_segments(hl7_data)
    patient_info, obx_data = extract_data(segments)

    st.subheader("👤 Patient Info")
    st.json(patient_info)

    if obx_data:
        df = pd.DataFrame(obx_data)
        st.subheader("🧪 Observations")
        st.dataframe(df)

        st.download_button("Download CSV", df.to_csv(index=False), "observations.csv", "text/csv")
        st.download_button("Download JSON", json.dumps(obx_data, indent=2), "observations.json", "application/json")
    else:
        st.info("No OBX segments found.")
