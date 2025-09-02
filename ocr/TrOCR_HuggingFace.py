import os
import io
import time
import pathlib
import re
import json
from typing import List, Tuple, Dict, Any

import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import numpy as np
from rapidfuzz.distance import Levenshtein
from rapidfuzz import fuzz

VERSION = "v11-pdf-only-fallback+accuracy"

# ---------------- Models ----------------
MODEL_CHOICES = [
    "microsoft/trocr-small-printed",
    "microsoft/trocr-base-printed",
    # Uncomment if needed:
    # "microsoft/trocr-small-handwritten",
    # "microsoft/trocr-base-handwritten",
]
GEN_MAX_LENGTH = 512

WHITELIST_CHARS = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,:;!?%&()[]{}<>@#$^*+-/=_'\"|`~€£¥°©®™\t\n"
)

PAGE_HEADER_REGEX = re.compile(r"^===\s*Page\s+(\d+)", re.IGNORECASE)
PAGE_SPLIT_TOKEN = "=== Page "

# ---------------- PDF Backends ----------------
PDF_BACKEND = "none"
PDF_BACKEND_ERROR = None
try:
    import pdf2image  # noqa: F401
    PDF_BACKEND = "pdf2image"
except Exception as e_pdf:
    try:
        import fitz  # noqa: F401
        PDF_BACKEND = "pymupdf"
    except Exception as e_pymu:
        PDF_BACKEND = "none"
        PDF_BACKEND_ERROR = f"pdf2image err: {e_pdf}; pymupdf err: {e_pymu}"

@st.cache_resource(show_spinner=True)
def load_trocr(model_id: str):
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    processor = TrOCRProcessor.from_pretrained(model_id)
    model = VisionEncoderDecoderModel.from_pretrained(model_id)
    model.eval()
    return processor, model

@st.cache_resource(show_spinner=False)
def load_unified_paddle(lang: str = "en"):
    from paddleocr import PaddleOCR
    return PaddleOCR(lang=lang, det=True, rec=True, cls=True)

def have_tesseract():
    try:
        import pytesseract  # noqa: F401
        return True
    except Exception:
        return False

def libgl_present() -> bool:
    for p in (
        "/usr/lib/x86_64-linux-gnu/libGL.so.1",
        "/usr/lib/libGL.so.1",
        "/usr/lib64/libGL.so.1",
        "/usr/local/lib/libGL.so.1"
    ):
        if os.path.exists(p):
            return True
    return False

# ---------------- Utility Functions ----------------
def pdf_to_images_pdf2image(pdf_bytes: bytes, dpi: int) -> List[Image.Image]:
    from pdf2image import convert_from_bytes
    return convert_from_bytes(pdf_bytes, dpi=dpi)

def pdf_to_images_pymupdf(pdf_bytes: bytes, dpi: int) -> List[Image.Image]:
    import fitz
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)
    pages = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        pages.append(img)
    return pages

def pdf_bytes_to_images(pdf_bytes: bytes, dpi: int) -> List[Image.Image]:
    if PDF_BACKEND == "pdf2image":
        return pdf_to_images_pdf2image(pdf_bytes, dpi)
    if PDF_BACKEND == "pymupdf":
        return pdf_to_images_pymupdf(pdf_bytes, dpi)
    raise RuntimeError("No PDF backend available.")

def resize_if_needed(img: Image.Image, max_dim: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= max_dim:
        return img
    scale = max_dim / float(longest)
    return img.resize((int(w * scale), int(h * scale)))

def non_white_ratio(img: Image.Image) -> float:
    arr = np.array(img.convert("L"))
    return float(np.sum(arr < 240) / arr.size)

def sanitize_text(text: str, enforce_whitelist: bool) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.rstrip() for line in t.splitlines())
    if enforce_whitelist:
        t = "".join(ch for ch in t if ch in WHITELIST_CHARS)
    return t.strip()

def preprocess_image(
    img: Image.Image,
    enable: bool,
    method: str,
    boost_contrast: bool,
    invert: bool,
    gamma: float
) -> Image.Image:
    if not enable:
        return img
    work = ImageOps.grayscale(img)
    if invert:
        work = ImageOps.invert(work)
    if boost_contrast:
        work = ImageOps.autocontrast(work)
        work = work.filter(ImageFilter.MedianFilter(size=3))
    if gamma != 1.0:
        arr = np.array(work).astype(np.float32) / 255.0
        arr = np.power(arr, gamma)
        work = Image.fromarray((arr * 255).clip(0, 255).astype("uint8"))
    if method == "otsu":
        work = otsu_binarize(work)
    elif method.startswith("fixed-"):
        thr = int(method.split("-")[1])
        work = fixed_threshold(work, thr)
    return work.convert("RGB")

def otsu_binarize(img_grey: Image.Image) -> Image.Image:
    arr = np.array(img_grey)
    hist, _ = np.histogram(arr.flatten(), bins=256, range=(0, 255))
    total = arr.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0.0
    best, thresh = 0, 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > best:
            best = var_between
            thresh = t
    bin_img = (arr > thresh).astype("uint8") * 255
    return Image.fromarray(bin_img)

def fixed_threshold(img_grey: Image.Image, thr: int) -> Image.Image:
    arr = np.array(img_grey)
    bin_img = (arr > thr).astype("uint8") * 255
    return Image.fromarray(bin_img)

def upscale_if_needed(img: Image.Image, enable: bool, factor: float, cap: int) -> Image.Image:
    if not enable or factor <= 1:
        return img
    w, h = img.size
    new_w, new_h = int(w * factor), int(h * factor)
    if max(new_w, new_h) > cap:
        scale = cap / float(max(new_w, new_h))
        new_w = int(new_w * scale)
        new_h = int(new_h * scale)
    return img.resize((new_w, new_h))

def trocr_page_ocr(img: Image.Image, processor, model) -> str:
    import torch
    pv = processor(images=img, return_tensors="pt").pixel_values
    with torch.inference_mode():
        out = model.generate(pv, max_length=GEN_MAX_LENGTH)
    return processor.batch_decode(out, skip_special_tokens=True)[0].strip()

def detect_lines_with_unified_paddle(paddle_obj, img: Image.Image):
    import numpy as np
    arr = np.array(img)
    res = paddle_obj.ocr(arr, det=True, rec=True, cls=True)
    lines = []
    if not res or not res[0]:
        return lines
    for entry in res[0]:
        polygon = entry[0]
        text, conf = entry[1]
        lines.append((polygon, text.strip(), conf))
    return lines

def line_crops_trocr(lines, original: Image.Image, processor, model,
                     min_height: int, upscale: float) -> List[str]:
    import torch
    results = []
    for polygon, _, _ in lines:
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        x0, x1 = int(max(min(xs), 0)), int(max(xs))
        y0, y1 = int(max(min(ys), 0)), int(max(ys))
        if x1 <= x0 or y1 <= y0:
            continue
        crop = original.crop((x0, y0, x1, y1))
        h = y1 - y0
        if h < min_height:
            crop = crop.resize((int(crop.width * upscale), int(crop.height * upscale)))
        pv = processor(images=crop, return_tensors="pt").pixel_values
        with torch.inference_mode():
            out_ids = model.generate(pv, max_length=256)
        txt = processor.batch_decode(out_ids, skip_special_tokens=True)[0].strip()
        if txt:
            results.append(txt)
    return results

def tesseract_ocr(img: Image.Image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"<<Tesseract not available: {e}>>"

def extract_pdf_text_vector(page_index: int, pdf_bytes: bytes) -> str:
    try:
        import fitz
    except Exception:
        return ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page_index < 0 or page_index >= len(doc):
        return ""
    return doc[page_index].get_text().strip()

# ---------------- Accuracy Helpers ----------------
def split_ocr_pages(full_text: str) -> List[str]:
    if PAGE_SPLIT_TOKEN not in full_text:
        return [full_text.strip()]
    pages = []
    current = []
    for line in full_text.splitlines():
        if PAGE_HEADER_REGEX.search(line):
            if current:
                pages.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        pages.append("\n".join(current).strip())
    return pages if pages else [full_text.strip()]

def split_gt_pages(gt_text: str) -> List[str]:
    return split_ocr_pages(gt_text)

def char_metrics(pred: str, ref: str) -> Dict[str, float]:
    ref_len = max(1, len(ref))
    dist = Levenshtein.distance(ref, pred)
    cer = dist / ref_len
    acc = 1.0 - cer
    ratio = fuzz.ratio(ref, pred) / 100.0
    return {
        "ref_chars": len(ref),
        "pred_chars": len(pred),
        "lev_char_distance": dist,
        "cer": cer,
        "char_accuracy": acc,
        "char_similarity_ratio": ratio
    }

def word_metrics(pred: str, ref: str) -> Dict[str, float]:
    ref_tokens = ref.split()
    pred_tokens = pred.split()
    ref_len = max(1, len(ref_tokens))
    dist = Levenshtein.distance(ref_tokens, pred_tokens)
    wer = dist / ref_len
    acc = 1.0 - wer
    ratio = fuzz.token_sort_ratio(ref, pred) / 100.0
    return {
        "ref_words": len(ref_tokens),
        "pred_words": len(pred_tokens),
        "lev_word_distance": dist,
        "wer": wer,
        "word_accuracy": acc,
        "word_similarity_ratio": ratio
    }

def compute_page_metrics(pred: str, ref: str) -> Dict[str, Any]:
    cm = char_metrics(pred, ref)
    wm = word_metrics(pred, ref)
    return {**cm, **wm}

def aggregate_global(pages_pred: List[str], pages_ref: List[str]) -> Dict[str, Any]:
    ref_all = "\n".join(pages_ref)
    pred_all = "\n".join(pages_pred)
    return compute_page_metrics(pred_all, ref_all)

def merge_macro(per_page: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_page:
        return {}
    agg = {}
    n = len(per_page)
    for key in per_page[0]:
        if isinstance(per_page[0][key], (int, float)):
            agg[key] = sum(p[key] for p in per_page) / n
    agg["pages_count"] = n
    return agg

# ---------------- UI ----------------
st.set_page_config(page_title="PDF OCR + Accuracy", layout="wide")
st.title("PDF OCR Pipeline – TrOCR + (Optional Paddle / Tesseract) + Vector + Accuracy")
st.caption(f"Version: {VERSION} (PDF ONLY)")

with st.sidebar:
    st.header("Model")
    model_id = st.selectbox("TrOCR Model", MODEL_CHOICES, index=1)

    st.header("PDF Rasterization")
    pdf_dpi = st.number_input("PDF DPI (render)", 72, 600, 200, 10)

    st.header("Scaling")
    max_dim = st.number_input("Max longest side after raster (px)", 512, 8000, 2200, 64)
    disable_resize = st.checkbox("Disable resize", False)
    page_upscale = st.checkbox("Upscale rendered page", False)
    page_upscale_factor = st.slider("Upscale factor", 1.0, 4.0, 1.6, 0.1, disabled=not page_upscale)
    page_upscale_cap = st.number_input("Upscale max dimension cap", 512, 12000, 3600, 64, disabled=not page_upscale)

    st.header("Preprocessing")
    enable_pre = st.checkbox("Enable preprocessing", True)
    pre_method = st.selectbox("Method", ["grayscale", "otsu", "fixed-160", "fixed-180", "fixed-200"], disabled=not enable_pre)
    boost_contrast = st.checkbox("Boost contrast + median", True, disabled=not enable_pre)
    invert = st.checkbox("Invert (light-on-dark)", False, disabled=not enable_pre)
    gamma = st.slider("Gamma", 0.2, 2.5, 1.0, 0.1, disabled=not enable_pre)

    st.header("Fallback Controls")
    enable_paddle = st.checkbox("Enable Paddle det+rec fallback", False)
    suppress_paddle_warning = st.checkbox("Suppress Paddle warnings", True, disabled=not enable_paddle)
    paddle_lang = st.text_input("Paddle language", "en", disabled=not enable_paddle)
    enable_line_trocr = st.checkbox("Line crop TrOCR (from Paddle boxes)", True, disabled=not enable_paddle)
    line_min_height = st.number_input("Line min height (px)", 5, 200, 18, 1, disabled=not (enable_paddle and enable_line_trocr))
    line_upscale = st.slider("Line upscale factor", 1.0, 4.0, 1.6, 0.1, disabled=not (enable_paddle and enable_line_trocr))
    enable_tesseract = st.checkbox("Enable Tesseract fallback", have_tesseract())
    min_chars_accept = st.number_input("Min chars to accept page", 1, 2000, 25, 1)
    fallback_vector_pdf = st.checkbox("Vector PDF text fallback (extract embedded)", True)

    st.header("Output / Debug")
    enforce_whitelist = st.checkbox("Enforce whitelist", False)
    separators = st.checkbox("Add page separators", True)
    show_previews = st.checkbox("Show first page (orig & processed)", True)
    show_attempts = st.checkbox("Show per-page attempt logs", True)
    low_content_threshold = st.slider("Low non-white threshold", 0.0, 0.05, 0.01, 0.001)
    show_sys_diag = st.checkbox("Show environment diagnostics", True)

    st.header("Accuracy (Ground Truth)")
    enable_accuracy = st.checkbox("Enable accuracy metrics", False)
    gt_file = gt_text_input = None
    if enable_accuracy:
        gt_file = st.file_uploader("Ground Truth (.txt)", type=["txt"])
        gt_text_input = st.text_area("Or paste GT text", height=160)
        show_per_page_metrics = st.checkbox("Show per-page metrics table", True)
        export_metrics = st.checkbox("Enable metrics export", True)

    st.markdown("---")
    process_btn = st.button("Run OCR", type="primary")
    clear_cache_btn = st.button("Clear caches")
    if clear_cache_btn:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Caches cleared.")

st.markdown("### Upload PDF")
uploaded = st.file_uploader("PDF only", type=["pdf"])

if uploaded is None or not process_btn:
    st.stop()

if not uploaded.name.lower().endswith(".pdf"):
    st.error("Non-PDF file provided. This app only processes PDF.")
    st.stop()

file_bytes = uploaded.read()
file_name = uploaded.name

processor, model = load_trocr(model_id)

# Paddle init
paddle_obj = None
paddle_init_error = ""
if enable_paddle:
    if not libgl_present() and not suppress_paddle_warning:
        st.warning("libGL.so.1 missing. Install libgl1 or switch to opencv-python-headless.")
    try:
        paddle_obj = load_unified_paddle(paddle_lang)
    except Exception as e:
        paddle_init_error = str(e)
        if not suppress_paddle_warning:
            st.warning(
                f"Paddle initialization failed: {paddle_init_error}\n"
                "Install opencv-python-headless OR system libgl1 (and ensure paddlepaddle installed)."
            )

# Rasterize PDF
try:
    if PDF_BACKEND == "none":
        raise RuntimeError("No PDF backend available (install pdf2image+poppler OR pymupdf).")
    pages = pdf_bytes_to_images(file_bytes, pdf_dpi)
except Exception as e:
    st.error(f"Rasterization failed: {e}")
    st.stop()

if not pages:
    st.error("No pages produced from PDF.")
    st.stop()

if show_previews:
    st.image(pages[0], caption=f"Original Page 1 size={pages[0].size}")

progress = st.progress(0, text="OCR in progress...")
page_texts: List[str] = []
attempt_logs: List[Dict[str, Any]] = []

for idx, page in enumerate(pages, 1):
    t_loop = time.time()
    try:
        working = page
        if not disable_resize:
            working = resize_if_needed(working, max_dim)
        if page_upscale:
            working = upscale_if_needed(working, True, page_upscale_factor, page_upscale_cap)
        processed = preprocess_image(working, enable_pre, pre_method, boost_contrast, invert, gamma)

        if idx == 1 and show_previews:
            st.image(processed, caption=f"Processed Page 1 size={processed.size}")

        nw_proc = non_white_ratio(processed)
        attempts = []
        final_text = ""
        chosen_stage = ""

        # Stage 1: Page-level TrOCR
        try:
            t0 = time.time()
            txt_page = trocr_page_ocr(processed, processor, model)
            attempts.append({"stage": "trocr_page", "len": len(txt_page), "secs": time.time()-t0})
            if len(txt_page) >= min_chars_accept:
                final_text = txt_page
                chosen_stage = "trocr_page"
        except Exception as e:
            attempts.append({"stage": "trocr_page", "error": str(e)})

        # Stage 2: Paddle
        lines = []
        if not final_text and paddle_obj:
            try:
                t0 = time.time()
                lines = detect_lines_with_unified_paddle(paddle_obj, processed)
                paddle_text = "\n".join(l[1] for l in lines)
                attempts.append({"stage": "paddle_full", "lines": len(lines), "len": len(paddle_text), "secs": time.time()-t0})
                if len(paddle_text) >= min_chars_accept:
                    final_text = paddle_text
                    chosen_stage = "paddle_full"
                if not final_text and enable_line_trocr and lines:
                    t1 = time.time()
                    trocr_line_texts = line_crops_trocr(
                        lines, processed, processor, model,
                        min_height=line_min_height, upscale=line_upscale
                    )
                    merged_line_text = "\n".join(trocr_line_texts)
                    attempts.append({
                        "stage": "line_trocr",
                        "lines_in": len(lines),
                        "decoded": len(trocr_line_texts),
                        "len": len(merged_line_text),
                        "secs": time.time()-t1
                    })
                    if len(merged_line_text) >= min_chars_accept:
                        final_text = merged_line_text
                        chosen_stage = "line_trocr"
            except Exception as e:
                msg = str(e)
                if "libGL.so" in msg:
                    msg += " | Hint: install opencv-python-headless or libgl1"
                attempts.append({"stage": "paddle_full", "error": msg})

        # Stage 3: Tesseract
        if not final_text and enable_tesseract:
            try:
                t0 = time.time()
                tess = tesseract_ocr(processed).strip()
                attempts.append({"stage": "tesseract", "len": len(tess), "secs": time.time()-t0})
                if not tess.startswith("<<Tesseract not available") and len(tess) >= min_chars_accept:
                    final_text = tess
                    chosen_stage = "tesseract"
            except Exception as e:
                attempts.append({"stage": "tesseract", "error": str(e)})

        # Stage 4: Vector text
        if not final_text and fallback_vector_pdf:
            try:
                t0 = time.time()
                vec = extract_pdf_text_vector(idx - 1, file_bytes)
                attempts.append({"stage": "vector_pdf", "len": len(vec), "secs": time.time()-t0})
                if len(vec) >= min_chars_accept:
                    final_text = vec
                    chosen_stage = "vector_pdf"
            except Exception as e:
                attempts.append({"stage": "vector_pdf", "error": str(e)})

        if not final_text:
            if nw_proc > low_content_threshold:
                final_text = "<<NO TEXT DECODED (content suspected) – adjust DPI/preprocessing>>"
            else:
                final_text = "<<PAGE LIKELY BLANK>>"

        final_text = sanitize_text(final_text, enforce_whitelist)
        page_texts.append(final_text)
        attempt_logs.append({
            "page": idx,
            "chosen_stage": chosen_stage or "none",
            "attempts": attempts,
            "non_white_processed": round(nw_proc, 5),
            "size_processed": processed.size
        })
        progress.progress(idx / len(pages), text=f"Page {idx}/{len(pages)} ({time.time()-t_loop:.1f}s)")
    except Exception as e:
        page_texts.append(f"<<ERROR {e}>>")
        attempt_logs.append({"page": idx, "error": str(e)})
        progress.progress(idx / len(pages), text=f"Error page {idx}")

progress.progress(1.0, text="Complete")

# Combine output
if separators and len(pages) > 1:
    combined = "\n\n".join(
        f"=== Page {m['page']} (stage={m.get('chosen_stage','?')}) ===\n{text}"
        for m, text in zip(attempt_logs, page_texts)
    )
else:
    combined = "\n\n".join(page_texts)

st.markdown("### OCR Result")
st.text_area("Text Output", combined, height=380)
st.download_button(
    "Download OCR Text",
    combined.encode("utf-8"),
    file_name=f"{pathlib.Path(file_name).stem}_ocr.txt",
    mime="text/plain"
)

# ---------------- Accuracy Evaluation ----------------
if enable_accuracy:
    st.markdown("### Accuracy Evaluation")
    if gt_file is not None:
        gt_raw = gt_file.read().decode("utf-8", errors="replace")
    else:
        gt_raw = gt_text_input or ""
    if not gt_raw.strip():
        st.info("No Ground Truth provided.")
    else:
        ocr_pages = split_ocr_pages(combined)
        gt_pages = split_gt_pages(gt_raw)
        overlap = min(len(ocr_pages), len(gt_pages))
        per_page_metrics = []
        for i in range(overlap):
            pm = compute_page_metrics(ocr_pages[i], gt_pages[i])
            pm["page"] = i + 1
            per_page_metrics.append(pm)

        macro = merge_macro(per_page_metrics)
        overall = aggregate_global(ocr_pages[:overlap], gt_pages[:overlap])

        st.write(f"OCR pages: {len(ocr_pages)} | GT pages: {len(gt_pages)} | Overlap: {overlap}")
        if per_page_metrics and show_per_page_metrics:
            import pandas as pd
            df = pd.DataFrame(per_page_metrics)
            ordered = [
                "page",
                "ref_chars","pred_chars","lev_char_distance","cer","char_accuracy","char_similarity_ratio",
                "ref_words","pred_words","lev_word_distance","wer","word_accuracy","word_similarity_ratio"
            ]
            df = df[[c for c in ordered if c in df.columns]]
            st.dataframe(df, use_container_width=True)
        st.subheader("Macro (Unweighted)")
        st.json(macro)
        st.subheader("Overall (Concatenated)")
        st.json(overall)

        if len(ocr_pages) != len(gt_pages):
            st.warning("GT page count differs from OCR page count; only overlapping pages evaluated.")

        if export_metrics and per_page_metrics:
            metrics_bundle = {
                "version": VERSION,
                "file": file_name,
                "pages_overlap": overlap,
                "per_page": per_page_metrics,
                "macro": macro,
                "overall": overall
            }
            jb = json.dumps(metrics_bundle, indent=2).encode("utf-8")
            st.download_button(
                "Download Metrics JSON",
                jb,
                file_name=f"{pathlib.Path(file_name).stem}_metrics.json",
                mime="application/json"
            )
            import pandas as pd
            df_csv = pd.DataFrame(per_page_metrics)
            csv_buf = io.StringIO()
            df_csv.to_csv(csv_buf, index=False)
            st.download_button(
                "Download Per-Page Metrics CSV",
                csv_buf.getvalue().encode("utf-8"),
                file_name=f"{pathlib.Path(file_name).stem}_page_metrics.csv",
                mime="text/csv"
            )

# Attempt logs
if show_attempts:
    st.markdown("### Attempt Logs")
    for meta, text in zip(attempt_logs, page_texts):
        with st.expander(f"Page {meta['page']} details"):
            st.json(meta)
            st.write("Excerpt:", text[:400])

# Diagnostics
if show_sys_diag:
    st.markdown("### Environment Diagnostics")
    diag = {
        "version": VERSION,
        "python_version": os.sys.version.split()[0],
        "pdf_backend": PDF_BACKEND,
        "pdf_backend_error": PDF_BACKEND_ERROR,
        "paddle_requested": enable_paddle,
        "paddle_enabled": bool(paddle_obj),
        "paddle_init_error": paddle_init_error if (enable_paddle and not suppress_paddle_warning) else ("(suppressed)" if paddle_init_error else ""),
        "tesseract_available": have_tesseract(),
        "libGL_present": libgl_present(),
        "pages": len(pages),
        "dpi": pdf_dpi
    }
    st.json(diag)

st.caption(
    "PDF-only OCR pipeline. Increase PDF DPI or enable Paddle/Tesseract if page-level TrOCR misses text. "
    "Accuracy metrics require matching Ground Truth."
)
