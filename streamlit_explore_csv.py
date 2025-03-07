#command line: streamlit run streamlit_explore_csv.py
#Lauched: https://visual-csv.streamlit.app/
import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

uploaded_file = st.file_uploader("Choose a CSV file")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    #st.write(bytes_data)
    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    #st.write(stringio)
    # To read file as string:
    string_data = stringio.read()
    #st.write(string_data)
    
    # Read file as DataFrame
    df = pd.read_csv(uploaded_file)    
    # Fill 'None' values with 0
    df = df.fillna(0)
    
        # Select numerical columns only
    num_cols = df.select_dtypes(include=['number'])
        
    # Display basic statistics
    if not num_cols.empty:
        st.write("### Summary Statistics:")
        st.write(num_cols.describe())  # Shows count, mean, std, min, max, etc.

        # Option to choose a column and display its statistics
        selected_col = st.selectbox("Select a column to view details:", num_cols.columns)
        st.write(f"### Statistics for {selected_col}:")
        st.write(num_cols[selected_col].describe())            
    else:
        st.warning("No numerical columns found in the dataset.")
        
    # Check if "Period" column exists
    if "Period" in df.columns:
        #df["Period"] = df["Period"].astype(int)  # Ensure Period is integer

        # Slider range based on min and max values in the "Period" column[YYYY.MM]
        min_val, max_val = int(df["Period"].min()), int(df["Period"].max())
        st.write("### Period Range Slider:")
        period_range = st.slider("You may pick Period range:", min_val, max_val, (min_val, max_val))

        # Filter data based on slider range
        filtered_data = df[(df["Period"] >= period_range[0]) & (df["Period"] <= period_range[1])]
        filtered_data = filtered_data.fillna(0)
        st.write(filtered_data)

        # Check if "Data_value" column exists before plotting
        if "Data_value" in df.columns:
            # Create a line chart using Altair
            chart_line = alt.Chart(filtered_data).mark_line().encode(x='Period:O',y='Data_value:Q',tooltip=['Period', 'Data_value']).properties(width=700, height=400)
            # Create box chart using Altair
            chart_box = alt.Chart(filtered_data).mark_boxplot().encode(x='Period:O',y='Data_value:Q',tooltip=['Period', 'Data_value']).properties(width=700, height=400)
            # Create HeatMap
            chart_rule= alt.Chart(filtered_data).mark_rule(color="red").encode(x='Period:O',y='Data_value:Q',tooltip=['Period', 'Data_value']).properties(width=700, height=400)

            # Display the chart in Streamlit
            st.write("### Altair Charts:")
            st.altair_chart(chart_line, use_container_width=True)
            st.altair_chart(chart_box)
            st.altair_chart(chart_rule)
        else:
            st.error("Column 'Data_value' not found in the uploaded file.")
    else:
        st.write(df)
        # Select numerical columns only
        num_cols = df.select_dtypes(include=['number']).drop(columns=["ID"], errors="ignore")
        
        # Display basic statistics
        if not num_cols.empty:
            st.write("### Summary Statistics:")
            st.write(num_cols.describe())  # Shows count, mean, std, min, max, etc.
        
            # Option to choose a column and display its statistics
            selected_col = st.selectbox("Select a column to view details:", num_cols.columns)
            st.write(f"### Statistics for {selected_col}:")
            st.write(num_cols[selected_col].describe())            
            
             # Select columns for plotting
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if len(numeric_cols) >= 2:
                x_axis = st.selectbox("Select X-axis:", numeric_cols)
                y_axis = st.selectbox("Select Y-axis:", numeric_cols, index=1)

                # Create chart
                chart = alt.Chart(df).mark_line().encode(
                    x=f"{x_axis}:Q",
                    y=f"{y_axis}:Q",
                    tooltip=[x_axis, y_axis]
                ).properties(title=f"{y_axis} over {x_axis}", width=700, height=400)

                # Show chart
                st.altair_chart(chart, use_container_width=True)
        else:
              st.error("Not enough numerical columns to generate a chart.")
       