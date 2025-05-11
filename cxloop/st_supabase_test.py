from supabase import create_client
import streamlit as st

sb_url = st.secrets["supabase"]["url"]
anon_key = st.secrets["supabase"]["key"]
supabase = create_client(sb_url, anon_key)

# Fetch data from a table
response = supabase.table("public.users").select("*").execute()

st.write(response.data)