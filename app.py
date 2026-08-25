import streamlit as st
import tempfile
import shutil
from pathlib import Path

from pdf_to_csv import process_pdf

st.set_page_config(page_title="PDF to CSV", page_icon="📄", layout="centered")
st.title("📄 PDF to CSV Converter")
st.markdown("Upload PDF files containing player tables to extract data as CSV.")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files and st.button("Convert to CSV"):
    output_dir = Path(tempfile.mkdtemp())
    output_dir.mkdir(parents=True, exist_ok=True)

    progress = st.progress(0, text="Processing...")

    for i, uploaded in enumerate(uploaded_files):
        progress.progress((i) / len(uploaded_files), text=f"Processing {uploaded.name}...")

        tmp_path = output_dir / uploaded.name
        tmp_path.write_bytes(uploaded.getvalue())

        try:
            process_pdf(tmp_path, output_dir)
        except Exception as e:
            st.error(f"Error processing {uploaded.name}: {e}")
            continue

    progress.progress(1.0, text="Done!")

    csv_files = list(output_dir.glob("*.csv"))
    if csv_files:
        st.success(f"Converted {len(csv_files)} file(s)")
        for csv_file in csv_files:
            with open(csv_file, "rb") as f:
                st.download_button(
                    label=f"⬇ Download {csv_file.name}",
                    data=f,
                    file_name=csv_file.name,
                    mime="text/csv",
                )
    else:
        st.warning("No tables found in uploaded PDFs.")

    shutil.rmtree(output_dir, ignore_errors=True)
