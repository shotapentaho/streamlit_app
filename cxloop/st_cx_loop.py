hide_default_header = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
hide_default_footer = """
    <style>
    footer, .st-emotion-cache-1gulkj5 {display: none; visibility: hidden;}
    .css-qri22k {display: none; visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_link__1S137 {display: none;}
    </style>
"""
hide_github_icon = """
    <style>
        .viewerBadge_container__1QSob,
        .viewerBadge_link__1S137,
        .viewerBadge_text__1JaDK,
        #MainMenu,
        footer {
            display: none !important;
        }
    </style>
"""
import streamlit as st
st.set_page_config(page_title="Customer Xperiences..", layout="wide")
st.markdown(hide_default_footer, unsafe_allow_html=True)
st.markdown(hide_default_header, unsafe_allow_html=True)
st.markdown(hide_github_icon, unsafe_allow_html=True)
import st_contractor_feedback
import st_contractor_view_analyze


if len(st.query_params)> 1:
     # Update session state based on the URL parameter
    if st.query_params["logged_in"] == "true":
        st.session_state.logged_in = True      
else:
    st.session_state.logged_in = False
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "logout_triggered" not in st.session_state:
    st.session_state.logout_triggered = False
    
# --- TOP RIGHT LOGOUT BUTTON ---
top_col1, top_col2 = st.columns([8, 1])
with top_col2:
    # Log out and redirect to another app/page
    if st.button("Loogout"):
        st.session_state.logged_in = False
        st.markdown("""
            <script>
                window.location.href = "https://cxloop.co/";
            </script>
        """, unsafe_allow_html=True)
        st.stop()

# --- Main content if still logged in ---
if st.session_state.get("logged_in"):
    cxloop_tabs = st.tabs(["Feedback Entry", "Query all feedbacks "])

    with cxloop_tabs[0]:
        st_contractor_feedback.render()

    with cxloop_tabs[1]:
        st_contractor_view_analyze.render()


