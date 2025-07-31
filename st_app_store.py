import streamlit as st

st.set_page_config(page_title="Hot-Store", layout="wide")

# Streamlit app title
st.title("🔥 Hot apps @ hot-store 🚀")

# Dictionary of Streamlit URLs (Replace with your actual links)
st_generic_urls = {
    "☀️☁️❄️🧭 weather, map, AQI":"https://climate-weather.streamlit.app/",
    "🌨️Air Quality Only":"https://breathe-quality.streamlit.app/",
    "🌍🕰️ Analog clocks global":"https://samaya.streamlit.app/",
    "📫 Autofill US Address" : "https://us-address-autofill.streamlit.app/",
    "🔁 Converter MKS↔FPS, Force-Energy-Pressure-Temp ":"https://convert-units-now.streamlit.app/",
    "🎾 Game Reminder(SMS - Only US/CA)":"https://game-practice-reminder.streamlit.app/",
    "📈Explore CSV": "https://visual-csv.streamlit.app/", 
	"📈Simple and Compound interest": "https://viz-simple-compound-interest.streamlit.app/",	
    "📈Linear Equation": "https://viz-linear-eqn.streamlit.app/",
	"📈Quadratic Equation": "https://graphquadratic.streamlit.app/",
    "📐Area of Sector (Circle)":"https://circle-sector.streamlit.app/",
    "Triangle by co-ordinates": "https://viz-triangle.streamlit.app/",
    "Multi Log Curves": "https://viz-logarithm.streamlit.app/",
    "📐Trigonometry Visualizer":"https://trigonometry.streamlit.app/",
    "HL7-Health Level Seven to CSV Parser":"https://parse-hl7-emr.streamlit.app/"
}

st_ml_dl_urls = {
    "🚗 Auto Manual PDF (Text Embedding) via LLMs [Openai and Gemini]": "https://auto-manual-search.cxloop.co/",
    "📄🧠 NLP (English) on DuckDB: Analyze and Visualize CSV/JSON": "https://nlp-query-duckdb.streamlit.app/",
    "FAISS RAG - Upload and search your PDF! 🚀": "https://faiss-rag.cxloop.co/",
    "LLM Agent: LangGraph orchestration and LangSmith with OpenAI LLM": "https://agent-ai-lg-trace.streamlit.app/",
    "NLP NER - Named Entity Recognition":"https://ner-from-text.streamlit.app/",
    "NLP Translator - Human Languages": "https://translate-language.streamlit.app/",
    "NLP Sentiment analysis - Hugging Face pipeline":"https://get-sentiment.streamlit.app/",
    "NLP Sentiment Analysis - by models": "https://analyze-sentiment.streamlit.app/",
    "NLP Summarize Text": "https://summarize-info.streamlit.app/",
    "PyMuPDF - PDF Text Extractor":"https://pdf-to-txt.streamlit.app/",
    "DL Detect Bone Fracture": "https://detect-bone-fracture.streamlit.app/",
    "DL Detect Mood from Selfie":"https://detect-mood-selfie.streamlit.app/",
    "ML 📈 Classifier - Decision Tree Classifier": "https://hot-decision-tree.streamlit.app/",
	"ML 📈 Clustering K-Means": "https://hot-kmeans-clustering.streamlit.app/",
	"ML 📈 Linear Regression": "https://hot-linear-regression.streamlit.app/",
	"ML 📈 Classifier - Logistic Regression": "https://hot-logistic-regression.streamlit.app/",
    "ML 📈 Classifier - SVM ": "https://viz-svm-classifier.streamlit.app/",
	"LLM Bot powered by OpenAI": "https://openai-hot-bot.streamlit.app/",
    "ML Dim Reduction: SOM Unsupervised":"https://self-org-map.streamlit.app/"
   }
# Create two columns
col1, col2, col3 = st.columns([4,2,4])

with col3:

    # Dropdown or radio button for selection
    st.markdown(
    "<h3 style='text-align: left; color: red;'>Select an utility app here:</h3>",
    unsafe_allow_html=True
    )
    page_generic = st.selectbox("", list(st_generic_urls.keys()))

    # Button to open the selected page
    if st.button("Go to Site"):
        st.markdown(f"[Click here to open {page_generic}]({st_generic_urls[page_generic]})", unsafe_allow_html=True)
        st.write("The link will open in a new tab.")

    # Optional: Display all links as clickable buttons
    st.subheader("Quick Links:")

    # Create dynamic columns based on the number of links
    num_columns = 2  # Adjust this number for different layouts
    links = list(st_generic_urls.items())

    for i in range(0, len(links), num_columns):
        cols = st.columns(num_columns)  # Create columns dynamically
        for col, (name, url) in zip(cols, links[i:i+num_columns]):
            col.markdown(f"[{name}]({url})", unsafe_allow_html=True)  # Create a clickable link in each column

with col2:
    st.write("")

with col1:

    # Dropdown or radio button for selection
    #page_ml_dl = st.selectbox("Select your LLM, ML, DL app here:", list(st_ml_dl_urls.keys()))
    st.markdown(
    "<h3 style='text-align: left; color: red;'>Select Data Analysis, LLMs, NLP Apps, Deep Learning Apps, ML Algorithms with visuals more..</h3>",
    unsafe_allow_html=True
    )
    page_ml_dl = st.selectbox("", list(st_ml_dl_urls.keys()))

    # Button to open the selected page
    if st.button("Go to the Site"):
        st.markdown(f"[Click here to open {page_ml_dl}]({st_ml_dl_urls[page_ml_dl]})", unsafe_allow_html=True)
        st.write("The link will open in a new tab.")

    # Optional: Display all links as clickable buttons
    st.subheader("Quick Links:")

    # Create dynamic columns based on the number of links
    num_columns = 2  # Adjust this number for different layouts
    links = list(st_ml_dl_urls.items())

    for i in range(0, len(links), num_columns):
        cols = st.columns(num_columns)  # Create columns dynamically
        for col, (name, url) in zip(cols, links[i:i+num_columns]):
            col.markdown(f"[{name}]({url})", unsafe_allow_html=True)  # Create a clickable link in each column

