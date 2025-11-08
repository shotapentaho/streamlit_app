import streamlit as st
from PIL import Image
import io
import json
import pandas as pd
import re
import os

# Use the new OpenAI Python client (openai>=1.0.0)
from openai import OpenAI

# PDF support via PyMuPDF (fitz)
PYMUPDF_AVAILABLE = False
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except Exception:
    fitz = None

# OCR backends: prefer EasyOCR, fallback to pytesseract
EASYOCR_AVAILABLE = False
PYTESSERACT_AVAILABLE = False
easyocr = None
pytesseract = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    easyocr = None

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except Exception:
    pytesseract = None

st.set_page_config(page_title="Invoice Files Processor", layout="wide")
st.title("Multiple invoice files processor: export as csv/json")

st.markdown("""
This app performs OCR using EasyOCR (preferred) or pytesseract (fallback).
If neither OCR package is installed, the app will show instructions to install them.
"""
)

# Sidebar controls
st.sidebar.header("LLM / Options")
model_name = st.sidebar.selectbox("Model", options=["gpt-4", "gpt-4o", "gpt-3.5-turbo"], index=0)
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
use_agent = st.sidebar.checkbox("Use simple agent (calls same LLM)", value=False)
process_all_pdf = st.sidebar.checkbox("Process all PDF pages", value=False)

PROMPT = """You are a document parser. Given this OCR result from a receipt or invoice, extract the following fields:
- Invoice Number
- Date
- Vendor Name
- Total Amount

OCR Text:
{text}

Respond in JSON with exactly those keys: "invoice_number", "date", "vendor_name", "total_amount".
If a field is not found, use an empty string for the value.
"""

# Global OpenAI client instance (set in load_openai_key_from_secrets)
openai_client = None

@st.cache_resource
def init_easyocr_reader(lang_list=None):
    if not EASYOCR_AVAILABLE:
        raise RuntimeError("easyocr is not installed.")
    lang_list = lang_list or ["en"]
    try:
        return easyocr.Reader(lang_list, gpu=False)
    except Exception as e:
        raise RuntimeError(f"EasyOCR initialization failed: {e}")

def run_easyocr_read(reader, pil_image: Image.Image):
    try:
        res = reader.readtext(pil_image)
    except Exception as e:
        raise RuntimeError(f"EasyOCR readtext failed: {e}")
    texts = []
    for item in res:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            texts.append(item[1])
        elif isinstance(item, dict) and "text" in item:
            texts.append(item["text"])
        else:
            texts.append(str(item))
    combined = "\n".join(texts)
    return {"text": combined, "backend": "easyocr", "raw": res}

def run_pytesseract_read(pil_image: Image.Image):
    if not PYTESSERACT_AVAILABLE:
        raise RuntimeError("pytesseract is not installed.")
    try:
        txt = pytesseract.image_to_string(pil_image)
    except Exception as e:
        raise RuntimeError(f"pytesseract failed: {e}")
    return {"text": txt, "backend": "pytesseract", "raw": txt}

def run_ocr(pil_image: Image.Image):
    """
    Run OCR using EasyOCR (preferred) or pytesseract (fallback).
    """
    # Try EasyOCR first
    if EASYOCR_AVAILABLE:
        try:
            reader = init_easyocr_reader()
            return run_easyocr_read(reader, pil_image)
        except Exception:
            # Fall back to pytesseract if allowed
            pass

    if PYTESSERACT_AVAILABLE:
        return run_pytesseract_read(pil_image)

    raise RuntimeError(
        "No OCR backend available. Install easyocr (pip install easyocr) or pytesseract (pip install pytesseract) and ensure Tesseract binary is installed."
    )

def pdf_bytes_to_pil_images(pdf_bytes: bytes, dpi: int = 150):
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (fitz) not available. Install pymupdf to process PDFs.")

    imgs = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        imgs.append(img)
    doc.close()
    return imgs

def load_openai_key_from_secrets():
    """
    Try multiple strategies to obtain OpenAI API key:
    1) st.secrets["OPENAI_API_KEY"]
    2) st.secrets["openai"]["api_key"]
    3) parse .streamlit/secrets.toml (local file) using toml if present
    If found, create an OpenAI client (OpenAI()) so the new SDK is used.
    """
    global openai_client
    key = None
    # 1) st.secrets
    try:
        if hasattr(st, "secrets"):
            if "OPENAI_API_KEY" in st.secrets:
                key = st.secrets["OPENAI_API_KEY"]
            elif "openai" in st.secrets and "api_key" in st.secrets["openai"]:
                key = st.secrets["openai"]["api_key"]
    except Exception:
        pass

    # 2) .streamlit/secrets.toml fallback
    if not key:
        toml_path = os.path.join(".streamlit", "secrets.toml")
        if os.path.exists(toml_path):
            try:
                import toml
                parsed = toml.load(toml_path)
                key = parsed.get("OPENAI_API_KEY") or (parsed.get("openai") or {}).get("api_key")
            except Exception:
                pass

    # If we found a key, set env var and create client
    if key:
        os.environ["OPENAI_API_KEY"] = key
        try:
            openai_client = OpenAI(api_key=key)
        except Exception:
            # Fallback to client without explicit key (will read env)
            openai_client = OpenAI()

    # If no key found but environment var already set, create client
    elif os.environ.get("OPENAI_API_KEY"):
        try:
            openai_client = OpenAI()
        except Exception:
            openai_client = None

    return key

def call_llm_with_text(text: str, model: str, temp: float) -> str:
    global openai_client
    formatted = PROMPT.format(text=text)

    # Ensure client exists (attempt to initialize from env if not)
    if openai_client is None:
        if os.environ.get("OPENAI_API_KEY"):
            openai_client = OpenAI()
        else:
            raise RuntimeError("OpenAI API key not set. Put it in .streamlit/secrets.toml or set OPENAI_API_KEY env var.")

    try:
        resp = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": formatted}],
            temperature=temp,
            max_tokens=1000,
        )
        # Extract content robustly for both dict and attribute-style responses
        try:
            content = resp["choices"][0]["message"]["content"]
        except Exception:
            try:
                content = resp.choices[0].message.content
            except Exception:
                content = json.dumps(resp, default=str)
        return content
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")

def extract_json_from_text(resp_text: str) -> dict:
    try:
        return json.loads(resp_text)
    except json.JSONDecodeError:
        m = re.search(r"(\{[\s\S]*\})", resp_text)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        return {"parse_error": True, "raw_response": resp_text}

def make_csv_bytes_from_list(data_list: list) -> bytes:
    df = pd.DataFrame(data_list)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")

# Load OpenAI key from Streamlit secrets or .streamlit/secrets.toml (quiet: no success message)
openai_key = load_openai_key_from_secrets()
if not openai_key and not os.environ.get("OPENAI_API_KEY"):
    st.warning(
        "OpenAI API key not found in Streamlit secrets. Create .streamlit/secrets.toml with OPENAI_API_KEY or add it via Streamlit sharing UI."
    )

# Two-column layout always visible: left = file browsing/scan, right = parsed output + downloads
left_col, right_col = st.columns([2, 1])

# Left column: file uploader (multiple), image preview, OCR + LLM invocation per file
with left_col:
    uploaded_files = st.file_uploader(
        "Browse files to scan (images or PDFs) — select multiple",
        type=["png", "jpg", "jpeg", "tiff", "bmp", "pdf"],
        accept_multiple_files=True,
    )

    parsed_list = []  # will contain parsed dict per file
    combined_texts = {}  # store combined_text by filename for agent use

    if uploaded_files:
        for uploaded_file in uploaded_files:
            filename = getattr(uploaded_file, "name", "uploaded")
            is_pdf = filename.lower().endswith(".pdf") or getattr(uploaded_file, "type", "").lower() == "application/pdf"

            pil_images = []
            try:
                if is_pdf:
                    pdf_bytes = uploaded_file.read()
                    if not PYMUPDF_AVAILABLE:
                        st.error(f"PDF uploaded ({filename}) but PyMuPDF (pymupdf) is not installed. Install pymupdf to process PDFs.")
                        continue
                    try:
                        imgs = pdf_bytes_to_pil_images(pdf_bytes, dpi=150)
                        if not imgs:
                            st.error(f"No images extracted from PDF: {filename}")
                            continue
                        if process_all_pdf:
                            pil_images = imgs
                        else:
                            pil_images = [imgs[0]]
                    except Exception as e:
                        st.error(f"Failed to convert PDF to images ({filename}): {e}")
                        continue
                else:
                    image = Image.open(uploaded_file).convert("RGB")
                    pil_images = [image]
            except Exception as e:
                st.error(f"Unable to open the uploaded file ({filename}): {e}")
                continue

            # Display image preview for this file
            st.image(pil_images[0], caption=f"{filename} — preview", use_container_width=True)

            # OCR for this file (first page or all pages)
            ocr_texts = []
            ocr_raw_pages = []
            ocr_backends = []
            for idx, img in enumerate(pil_images):
                try:
                    out = run_ocr(img)
                    ocr_texts.append(out.get("text", ""))
                    ocr_raw_pages.append(out.get("raw"))
                    ocr_backends.append(out.get("backend"))
                except Exception as e:
                    st.error(f"OCR failed on file {filename} page {idx+1}: {e}")
                    ocr_texts.append("")
                    ocr_raw_pages.append(None)
                    ocr_backends.append("ocr-error")

                if not process_all_pdf:
                    break

            combined_text = "\n\n".join(
                [f"--- PAGE {i+1} (backend={ocr_backends[i]}) ---\n{t}" for i, t in enumerate(ocr_texts)]
            )

            combined_texts[filename] = combined_text
            ocr_output = {"text": combined_text, "backend_pages": ocr_backends, "raw_pages": ocr_raw_pages}

            # Call LLM to parse this file (one call per file)
            try:
                llm_response_text = call_llm_with_text(combined_text, model_name, temperature)
                parsed = extract_json_from_text(llm_response_text)
            except Exception as e:
                parsed = {"parse_error": True, "raw_response": str(e)}

            # Ensure standard keys exist and attach filename
            parsed_record = {
                "filename": filename,
                "invoice_number": parsed.get("invoice_number", "") if isinstance(parsed, dict) else "",
                "date": parsed.get("date", "") if isinstance(parsed, dict) else "",
                "vendor_name": parsed.get("vendor_name", "") if isinstance(parsed, dict) else "",
                "total_amount": parsed.get("total_amount", "") if isinstance(parsed, dict) else "",
            }
            # If parsing failed, include raw_response for troubleshooting
            if isinstance(parsed, dict) and parsed.get("parse_error"):
                parsed_record["parse_error"] = True
                parsed_record["raw_response"] = parsed.get("raw_response", "")
            parsed_list.append(parsed_record)

# New: if any parsed record lacks an invoice_number, show only the error and stop further rendering
if parsed_list:
    missing_invoice = [r for r in parsed_list if not r.get("invoice_number")]
    if missing_invoice:
        st.error("Supply invoice to process")
        st.stop()

# Right column: Parsed Output (JSON list) and aggregated download buttons
with right_col:
    st.subheader("Parsed Output (JSON) — aggregated for all uploaded files")
    if parsed_list:
        st.json(parsed_list)
    else:
        st.info("Parsed output will appear here after uploading files.")

    # prepare bytes for download even if parsed_list is empty
    json_bytes = json.dumps(parsed_list, indent=2, ensure_ascii=False).encode("utf-8")
    csv_bytes = make_csv_bytes_from_list(parsed_list)
    st.download_button(
        label="Download-JSON",
        data=json_bytes,
        file_name="parsed_invoices.json",
        mime="application/json",
    )
    st.download_button(
        label="Download-CSV",
        data=csv_bytes,
        file_name="parsed_invoices.csv",
        mime="text/csv",
    )

# Agent: if requested, run agent per-file and show aggregated agent results and downloads
if use_agent and combined_texts:
    agent_results = []
    for fname, text in combined_texts.items():
        try:
            agent_resp = call_llm_with_text(text, model_name, temperature)
            agent_parsed = extract_json_from_text(agent_resp)
        except Exception as e:
            agent_parsed = {"parse_error": True, "raw_response": str(e)}
        rec = {
            "filename": fname,
            "invoice_number": agent_parsed.get("invoice_number", "") if isinstance(agent_parsed, dict) else "",
            "date": agent_parsed.get("date", "") if isinstance(agent_parsed, dict) else "",
            "vendor_name": agent_parsed.get("vendor_name", "") if isinstance(agent_parsed, dict) else "",
            "total_amount": agent_parsed.get("total_amount", "") if isinstance(agent_parsed, dict) else "",
        }
        if isinstance(agent_parsed, dict) and agent_parsed.get("parse_error"):
            rec["parse_error"] = True
            rec["raw_response"] = agent_parsed.get("raw_response", "")
        agent_results.append(rec)

    st.subheader("Agent parsed aggregated (JSON)")
    st.json(agent_results)
    st.markdown("**Agent Downloads (all files)**")
    agent_json_bytes = json.dumps(agent_results, indent=2, ensure_ascii=False).encode("utf-8")
    agent_csv_bytes = make_csv_bytes_from_list(agent_results)
    st.download_button(
        label="Download agent aggregated JSON",
        data=agent_json_bytes,
        file_name="agent_parsed_invoices.json",
        mime="application/json",
        key="agent_json_all",
    )
    st.download_button(
        label="Download agent aggregated CSV",
        data=agent_csv_bytes,
        file_name="agent_parsed_invoices.csv",
        mime="text/csv",
        key="agent_csv_all",
    )