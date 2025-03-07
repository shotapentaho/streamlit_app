#command line: streamlit run st_employment.py
#Lauched here: http://localhost:8501/
import streamlit as st
import pandas as pd
import altair as alt

input_file=r".\employment-small-size.csv"  # Use 'r' before the string to handle backslashes
st.write(""" # CSV file for data analysis! """)
st.write(input_file[35:len(input_file)])
 
df = pd.read_csv(input_file)
# Fill 'None' values with 0
df= df.fillna(0)
df_1000 = df.head(1000)
#st.write(df_1000)  --Debug

# Line Chart (defaults to index in X) - Started here to display in browser
#st.line_chart(df_1000[['Period', 'Data_value']])
#Fixed Slider(range) added!
#period_range = st.slider("period range!", 2005, 2025, (2010, 2021))

# Slider is dependent to data from "Period" column [YYYY.MM]
min_val, max_val = int(df["Period"].min()), int(df["Period"].max())
period_range = st.slider("Select Period range:", min_val, max_val, (min_val, max_val))

# Filter data based on slider range
filtered_data = df_1000[(df_1000['Period'] >= period_range[0]) & (df_1000['Period'] <= period_range[1]+1)]
filtered_data= filtered_data.fillna(0)
st.write(filtered_data)

# Create a line chart using Altair
chart = alt.Chart(filtered_data).mark_line().encode(x='Period:Q',  y='Data_value:Q',  tooltip=['Period', 'Data_value']).properties(width=700, height=400)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)