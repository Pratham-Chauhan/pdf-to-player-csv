import streamlit as st
from pathlib import Path
from pdf_to_csv import process_pdf  # Core PDF parsing logic
import tempfile
import shutil
import pandas as pd

st.set_page_config(page_title="PDF to CSV", page_icon="📄", layout="centered")
st.title("📄 PDF to CSV Converter")
st.markdown("Upload PDF files containing player tables to extract data as CSV.")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

# Persist converted results across Streamlit reruns (e.g. when download_button is clicked)
if "converted" not in st.session_state:
    st.session_state.converted = None

if uploaded_files and st.button("Convert to CSV", use_container_width=True):
    # Use a temp directory to hold intermediate CSV files
    output_dir = Path(tempfile.mkdtemp())
    output_dir.mkdir(parents=True, exist_ok=True)

    progress = st.progress(0, text="Processing...")

    for i, uploaded in enumerate(uploaded_files):
        progress.progress((i) / len(uploaded_files), text=f"Processing {uploaded.name}...")

        try:
            df = process_pdf(Path(uploaded.name), output_dir, file_bytes=uploaded.getvalue())

        except Exception as e:
            st.error(f"Error processing {uploaded.name}: {e}")
            continue

    progress.progress(1.0, text="Done!")

    csv_files = list(output_dir.glob("*.csv"))
    # Store results in session state so they survive download_button reruns
    st.session_state.converted = {"csv_files": csv_files, "output_dir": output_dir}

if st.session_state.converted:
    data = st.session_state.converted
    csv_files = data["csv_files"]
    output_dir = data["output_dir"]

    if csv_files:
        st.success(f"Converted {len(csv_files)} file(s)")

        for csv_file in csv_files:
            # Each file gets its own bordered container with preview and download
            with st.container(border=True):
            # with st.expander(f"**{csv_file.name}**", expanded=True):
                st.markdown(f"**{csv_file.name}**")

                df = pd.read_csv(csv_file)
                st.dataframe(df)
                with open(csv_file, "rb") as f:
                    with st.container(horizontal_alignment="right"):
                        st.download_button(
                            label=f"⬇ Download",
                            data=f,
                            file_name=csv_file.name,
                            mime="text/csv",
                            # Key must be unique per button to avoid Streamlit errors
                            key=f"download_{csv_file.name}", 
                        )

        if st.button("Clear Results"):
            # Reset state and clean up temp directory
            st.session_state.converted = None
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
            st.rerun()
    else:
        st.warning("No tables found in uploaded PDFs.")
