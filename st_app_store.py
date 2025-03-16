import streamlit as st

# Streamlit app title
st.title("Apps from Hot-Store 🚀")

# Description
#st.write("Select a page to visit and navigate to corresponding Streamlit apps.")

# Dictionary of Streamlit URLs (Replace with your actual links)
streamlit_urls = {
    "Explore CSV": "https://visual-csv.streamlit.app/", 
	"Simple and Compound interest": "https://viz-simple-compound-interest.streamlit.app/",	
	"Quadratic Equation": "https://graphquadratic.streamlit.app/",
    "Text Summarizer": "https://summarize-info.streamlit.app/",
    "Decision Tree Classifier": "https://hot-decision-tree.streamlit.app/",
	"K-Means Clustering": "https://hot-kmeans-clustering.streamlit.app/",
	"Linear Regression": "https://hot-linear-regression.streamlit.app/",
	"Logistic Regression": "https://hot-logistic-regression.streamlit.app/",
	"Bot powered by OpenAI": "https://openai-hot-bot.streamlit.app/"
}

# Dropdown or radio button for selection
page = st.selectbox("Select an app:", list(streamlit_urls.keys()))

# Button to open the selected page
if st.button("Go to Selected Page"):
    st.markdown(f"[Click here to open {page}]({streamlit_urls[page]})", unsafe_allow_html=True)
    st.write("The link will open in a new tab.")

# Optional: Display all links as clickable buttons
st.subheader("Quick Links:")

# Create dynamic columns based on the number of links
num_columns = 3  # Adjust this number for different layouts
links = list(streamlit_urls.items())

for i in range(0, len(links), num_columns):
    cols = st.columns(num_columns)  # Create columns dynamically
    for col, (name, url) in zip(cols, links[i:i+num_columns]):
        col.markdown(f"[{name}]({url})", unsafe_allow_html=True)  # Create a clickable link in each column
