# PDF to CSV Converter

A lightweight Python tool that extracts player table data (e.g., Men's, Women's, Youth rosters with Size, Number, and Names) from PDF documents and exports them to structured CSV files.

---

## 📦 Installation

Ensure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 CLI Usage (`pdf_to_csv.py`)

The primary interface is the `pdf_to_csv.py` CLI script. Converted CSV files are automatically saved to the `OUTPUT/` directory.

### 1. Process a Single PDF File

Provide the path to an individual PDF file:

```bash
python pdf_to_csv.py path/to/document.pdf
```

**Example:**
```bash
python pdf_to_csv.py INPUT/players.pdf
```

### 2. Batch Process All PDFs in a Directory

Use the `--all-pdfs` option followed by the directory containing PDF files:

```bash
python pdf_to_csv.py --all-pdfs <DIR>
```

**Example:**
```bash
python pdf_to_csv.py --all-pdfs INPUT
```

### CLI Options

| Argument / Option | Description |
| :--- | :--- |
| `input_file` | Path to a single input PDF file to process. |
| `--all-pdfs <DIR>` | Batch process all `.pdf` files in the specified directory. |
| `-h`, `--help` | Show command-line help message and exit. |

---

## 📂 Output

- Processed CSV files are saved in the `OUTPUT/` folder.
- The output file retains the input PDF base name with a `.csv` extension (e.g., `INPUT/sample.pdf` -> `OUTPUT/sample.csv`).
- Extracted columns typically include: `Size`, `#`, `Names`, and `Product` (category like *Men's*, *Women's*, or *Youth*).

---

## 🌐 Web Interface (Optional)

A simple Streamlit interface is also available:

```bash
streamlit run app.py
```
