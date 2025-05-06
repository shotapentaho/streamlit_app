import streamlit as st
import pandas as pd

def parse_hl7_to_segments(raw):
    segments = raw.strip().split("\n")
    return [line.strip().split("|") for line in segments if line.strip()]

def extract_data(segments):
    patient_info = {}
    combined_rows = []

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
            row = {
                **patient_info,
                "Observation ID": segment[3].split("^")[0] if len(segment) > 3 else "",
                "Observation Desc": segment[3].split("^")[1] if len(segment) > 3 and "^" in segment[3] else "",
                "Value": segment[5] if len(segment) > 5 else "",
                "Units": segment[6] if len(segment) > 6 else ""
            }
            combined_rows.append(row)

    return combined_rows

st.title("📄 HL7 to CSV Parser")

st.markdown("""
### 🧾 Sample HL7 Message Format

Here's a simplified HL7 message example:
MSH|^~\&|HIS|RIH|EKG|EKG|202405050930||ADT^A01|MSG00001|P|2.5
EVN|A01|202405050930
PID|1||123456^^^HOSP^MR||Doe^John||19800101|M|||123 Main St^^Anytown^NY^12345||555-1234
OBR|1||1001^LAB|88304^Pathology Exam^L
OBX|1|NM|1234-5^Hemoglobin^LN||14.5|g/dL|13.5-17.5|N|||F
OBX|2|NM|5678-9^WBC Count^LN||6.2|K/uL|4.0-10.0|N|||F
            
- Only `PID` and `OBX` are parsed.
- Other segments like `MSH`, `EVN`, `OBR` are ignored for now.
- Each `OBX` line represents one observation.

Please upload `.hl7` or `.txt` files in a similar format.
""")

uploaded_file = st.file_uploader("Upload your HL7 file", type=["hl7", "txt"])
if uploaded_file:
    hl7_data = uploaded_file.read().decode("utf-8")
    segments = parse_hl7_to_segments(hl7_data)
    combined_rows = extract_data(segments)

    if combined_rows:
        df = pd.DataFrame(combined_rows)
        st.subheader("👤📊 Combined Patient + Observation Data")
        st.dataframe(df)

        st.download_button("Download CSV", df.to_csv(index=False), "hl7_combined.csv", "text/csv")
    else:
        st.info("No OBX or PID segments found.")
