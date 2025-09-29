"""
UI theme helper for Streamlit apps.
Adds a light/dark toggle in the header and injects matching CSS.
Usage in your app:
    from ui_theme import apply_theme
    apply_theme()
"""

import streamlit as st

def apply_theme() -> bool:
    """
    Render a header toggle (🌞/🌙) and inject the corresponding CSS.
    Returns True if light mode is active, False if dark mode.
    """
    # Create three columns for the top header row; rightmost for the toggle
    top_left, top_center, top_right = st.columns([3, 1, 1])
    with top_right:
        if "light_mode" not in st.session_state:
            st.session_state.light_mode = True
        mode = st.toggle("🌞 / 🌙", value=st.session_state.light_mode, help="Switch light/dark theme")
        st.session_state.light_mode = mode

    style_holder = st.empty()

    light_css = """
    <style id="dynamic-theme">
    /* ---------- GLOBAL LIGHT RESET (v6) ---------- */
    :root {
      --app-bg: #ffffff;
      --app-fg: #000000;
      --panel-bg: #ffffff;
      --panel-border: #dcdfe3;
      --panel-hover: #f2f3f5;
      --accent: #3478f6;
      --accent-hover: #1f5fcc;
      --code-bg: #f5f5f5;
      --muted-fg: #444;
      --danger: #d93025;
      --success: #0f8a14;
      --warning: #b36b00;
      --radius-sm: 4px;
      --radius-md: 6px;
      --radius-lg: 10px;
      --shadow-none: none;

      /* Browse control accent (light only) — Beige palette (Coffee Cream) */
      --browse-accent: #8B6E54;
      --browse-accent-hover: #6E563F;

      /* v6: Darker uploader border (light only) */
      --uploader-border: #9aa0a6;
      --uploader-border-hover: #6e7278;
    }

    /* App root & main page area */
    .stApp,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
      background: var(--app-bg) !important;
      color: var(--app-fg) !important;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
      background: var(--panel-bg) !important;
      color: var(--app-fg) !important;
      border-right: 1px solid var(--panel-border) !important;
    }

    /* The inner scrolling content container */
    [data-testid="stSidebar"] .stSidebarContent {
      background: var(--panel-bg) !important;
      color: var(--app-fg) !important;
    }

    /* Remove any gradient/overlay pseudo-elements that some versions inject */
    [data-testid="stSidebar"]::before,
    [data-testid="stSidebar"]::after {
      background: none !important;
      content: "" !important;
      display: none !important;
    }

    /* Text inside sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] div {
      color: var(--app-fg) !important;
    }

    /* ---------- HEADERS / TEXT ---------- */
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stText"],
    div[data-testid="stHeader"],
    div[data-testid="stSubheader"],
    div[data-testid="stCaption"],
    p, span, label,
    h1, h2, h3, h4, h5, h6 {
      color: var(--app-fg) !important;
    }

    /* Muted text like captions */
    small, .stCaption, div[data-testid="stCaption"] {
      color: var(--muted-fg) !important;
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button,
    .stDownloadButton > button {
      background: #f2f2f5 !important;
      color: var(--app-fg) !important;
      border: 1px solid var(--panel-border) !important;
      border-radius: var(--radius-md) !important;
      box-shadow: var(--shadow-none) !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
      background: var(--panel-hover) !important;
      border-color: #b0b4b8 !important;
    }

    /* Primary colored buttons (if any) */
    button[kind="primary"] {
      background: var(--accent) !important;
      color: #fff !important;
      border: 1px solid var(--accent) !important;
    }
    button[kind="primary"]:hover {
      background: var(--accent-hover) !important;
    }

    /* ---------- CHECKBOX / TOGGLE / RADIO ---------- */
    [data-testid="stCheckbox"] input[type="checkbox"],
    [data-testid="stRadio"] input[type="radio"] {
      border: 1px solid #9da3aa !important;
    }
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {
      color: var(--app-fg) !important;
    }

    /* Toggle (stSwitch) */
    [data-testid="stToggle"] [role="checkbox"] {
      background: #e5e7ea !important;
      border: 1px solid #9da3aa !important;
      box-shadow: none !important;
    }
    [data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {
      background: var(--accent) !important;
      border-color: var(--accent-hover) !important;
    }
    [data-testid="stToggle"] [role="checkbox"] > div {
      background: #ffffff !important;
      box-shadow: none !important;
    }

    /* ---------- INPUTS (Text, Select, TextArea) ---------- */
    .stTextInput input,
    textarea,
    div[data-baseweb="select"] > div,
    .stTextArea textarea {
      background: #ffffff !important;
      color: var(--app-fg) !important;
      border: 1px solid var(--panel-border) !important;
      border-radius: var(--radius-sm) !important;
      box-shadow: none !important;
    }
    .stTextInput input:focus,
    textarea:focus,
    div[data-baseweb="select"] > div:focus,
    .stTextArea textarea:focus {
      border-color: var(--accent) !important;
      outline: 1px solid var(--accent) !important;
    }

    /* Select dropdown menu panel */
    [data-baseweb="popover"] {
      background: #ffffff !important;
      color: var(--app-fg) !important;
      border: 1px solid var(--panel-border) !important;
      box-shadow: none !important;
    }

    /* Multi-select tokens */
    div[data-baseweb="tag"] {
      background: #e8f0fe !important;
      color: #174ea6 !important;
      border-radius: var(--radius-sm) !important;
    }

    /* ---------- SLIDERS ---------- */
    .stSlider > div [role="slider"] {
      background: var(--accent) !important;
      border: 2px solid #ffffff !important;
    }
    .stSlider > div [data-baseweb="slider"] > div {
      background: #d0d4d9 !important;
    }
    .stSlider > div [data-baseweb="slider"] > div > div {
      background: var(--accent) !important;
    }

    /* ---------- CODE BLOCKS ---------- */
    div[data-testid="stCodeBlock"] pre,
    code {
      background: var(--code-bg) !important;
      color: #111 !important;
      border-radius: var(--radius-sm) !important;
    }

    /* ---------- EXPANDERS ---------- */
    details {
      background: var(--panel-bg) !important;
      color: var(--app-fg) !important;
      border: 1px solid var(--panel-border) !important;
      border-radius: var(--radius-md) !important;
    }
    summary {
      color: var(--app-fg) !important;
    }
    div.streamlit-expanderHeader {
      background: var(--panel-bg) !important;
      color: var(--app-fg) !important;
    }

    /* ---------- TABS ---------- */
    [data-baseweb="tab-list"] {
      background: transparent !important;
      border-bottom: 1px solid var(--panel-border) !important;
    }
    [data-baseweb="tab"] {
      color: var(--app-fg) !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
      color: var(--accent) !important;
      border-bottom: 2px solid var(--accent) !important;
    }

    /* ---------- SCROLLBAR ---------- */
    ::-webkit-scrollbar {
      width: 10px;
    }
    ::-webkit-scrollbar-track {
      background: var(--app-bg);
    }
    ::-webkit-scrollbar-thumb {
      background: #c0c3c7;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #a5a9ad;
    }

    /* ---------- TABLES / DATAFRAMES ---------- */
    [data-testid="stTable"] table,
    [data-testid="stDataFrame"] {
      background: #ffffff !important;
      color: var(--app-fg) !important;
    }
    [data-testid="stTable"] th,
    [data-testid="stTable"] td {
      border-color: var(--panel-border) !important;
    }

    /* ---------- ALERTS / STATUS BOXES ---------- */
    .stAlert {
      border-radius: var(--radius-md) !important;
      border: 1px solid var(--panel-border) !important;
    }

    /* ---------- FILE UPLOADER (LIGHT) ---------- */
    [data-testid="stFileUploader"] { color: var(--app-fg) !important; }
    [data-testid="stFileUploaderDropzone"] {
      background: var(--panel-bg) !important;
      color: var(--app-fg) !important;
      border: 2px dashed var(--uploader-border) !important;   /* v6 darker + thicker */
      border-radius: var(--radius-md) !important;
      transition: border-color 0.15s ease-in-out;
    }
    [data-testid="stFileUploaderDropzone"]:hover,
    [data-testid="stFileUploaderDropzone"]:focus-within {
      border-color: var(--uploader-border-hover) !important;  /* v6 hover/focus darker */
    }

    /* Ensure all inner text is visible */
    [data-testid="stFileUploaderDropzone"] * { color: var(--app-fg) !important; }

    /* Make "Browse files" clearly visible as link/label/button with beige color */
    [data-testid="stFileUploaderDropzone"] label,
    [data-testid="stFileUploaderDropzone"] a,
    [data-testid="stFileUploaderDropzone"] [role="button"] {
      color: var(--browse-accent) !important;
      font-weight: 600 !important;
      cursor: pointer !important;
    }
    [data-testid="stFileUploaderDropzone"] label:hover,
    [data-testid="stFileUploaderDropzone"] a:hover,
    [data-testid="stFileUploaderDropzone"] [role="button"]:hover {
      color: var(--browse-accent-hover) !important;
      text-decoration: underline !important;
    }

    /* Force the Browse control color across possible render variants */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploaderDropzone"] [data-baseweb="button"],
    [data-testid="stFileUploaderDropzone"] [role="button"],
    [data-testid="stFileUploaderDropzone"] label span,
    [data-testid="stFileUploader"] input[type="file"]::file-selector-button {
      color: var(--browse-accent) !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      text-decoration: none !important;
      cursor: pointer !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploaderDropzone"] [data-baseweb="button"]:hover,
    [data-testid="stFileUploaderDropzone"] [role="button"]:hover,
    [data-testid="stFileUploaderDropzone"] label:hover span,
    [data-testid="stFileUploader"] input[type="file"]::file-selector-button:hover {
      color: var(--browse-accent-hover) !important;
      text-decoration: underline !important;
    }

    /* Uploaded file info */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileInfo"],
    [data-testid="stFileUploader"] li,
    [data-testid="stFileUploader"] .uploadedFileData {
      color: var(--app-fg) !important;
    }

    /* ---------- MISC ---------- */
    hr { border-color: var(--panel-border) !important; }
    [class*="st-emotion-cache"][class*="elevation"] { box-shadow: none !important; }
    </style>
    """

    dark_css = """
    <style id="dynamic-theme">
    .stApp, body, [data-testid="stAppViewContainer"] {
      background: #0f1115 !important;
      color: #f5f7fa !important;
    }

    div[data-testid="stMarkdownContainer"],
    div[data-testid="stText"],
    div[data-testid="stHeader"],
    div[data-testid="stSubheader"],
    div[data-testid="stCaption"],
    p, span, label, h1, h2, h3, h4, h5, h6 {
      color: #f5f7fa !important;
    }

    .stButton > button, .stDownloadButton > button {
      background: #1f2329 !important;
      color: #f5f7fa !important;
      border: 1px solid #343a40 !important;
      box-shadow: none !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
      background: #2a3037 !important;
      border-color: #4a525a !important;
    }
    [data-testid="stToggle"] [role="checkbox"] {
      background: #2b3036 !important;
      border: 1px solid #4b535c !important;
    }
    [data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {
      background: #4d8dff !important;
      border-color: #72a6ff !important;
    }
    [data-testid="stToggle"] [role="checkbox"] > div {
      background: #ffffff !important;
    }

    /* Code blocks */
    div[data-testid="stCodeBlock"] pre, code {
      background: #1e2227 !important;
      color: #e3e8ef !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
      background: #1c2025 !important;
      color: #f5f7fa !important;
      border: 1px solid #3a4047 !important;
    }

    /* File Uploader (DARK) */
    [data-testid="stFileUploader"] { color: #e3e8ef !important; }
    [data-testid="stFileUploaderDropzone"] {
      background: #1c2025 !important;
      color: #e3e8ef !important;
      border: 1px dashed #3a4047 !important;
      border-radius: 6px !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: #e3e8ef !important; }
    [data-testid="stFileUploaderDropzone"] label,
    [data-testid="stFileUploaderDropzone"] a,
    [data-testid="stFileUploaderDropzone"] [role="button"] {
      color: #72a6ff !important;
      font-weight: 600 !important;
      cursor: pointer !important;
    }
    [data-testid="stFileUploaderDropzone"] label:hover,
    [data-testid="stFileUploaderDropzone"] a:hover,
    [data-testid="stFileUploaderDropzone"] [role="button"]:hover {
      color: #a9c6ff !important;
      text-decoration: underline !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #0f1115; }
    ::-webkit-scrollbar-thumb { background: #3a4047; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4c545d; }
    </style>
    """

    style_holder.markdown(light_css if st.session_state.light_mode else dark_css, unsafe_allow_html=True)
    return st.session_state.light_mode