
import streamlit as st
import st_contractor_feedback
import st_contractor_view_analyze

st.set_page_config(page_title="Customer Xperiences..", layout="wide")

if len(st.query_params)> 1:
     # Update session state based on the URL parameter
    if st.query_params["logged_in"] == "true":
        st.session_state.logged_in = True      
else:
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False

# --- TOP RIGHT LOGOUT BUTTON ---
top_col1, top_col2 = st.columns([8, 1])
with top_col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logging out...")
        # Inject JavaScript redirect
        st.markdown("""
            <script>
                window.location.href = "https://cxloop.co";
            </script>
        """, unsafe_allow_html=True)
        st.stop()


cxloop_tabs = st.tabs(["Feedback Entry", "Query all feedbacks "])

with cxloop_tabs[0]:
    st_contractor_feedback.render()

with cxloop_tabs[1]:
    st_contractor_view_analyze.render()


