import os
import io
import traceback
from typing import List, Union

import pdfplumber
import pandas as pd
from pathlib import Path
import argparse

try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = ""
    RED = ""
    BLUE = ""
    RESET = ""


# Check if any cell in the header row contains the given category string
find_table_by_category = (lambda catg, row: any([catg in x.strip() for x in row if x]))


def process_table_data(tdata, catg) -> pd.DataFrame:
    df = pd.DataFrame(tdata[2:], columns=tdata[1])

    columns_list = df.columns.to_list()
    ALLOWED_COLUMNS = ['Size', '#', 'Names']
    # Keep only expected columns; fall back to all columns if none match
    selected_cols = [i for i in columns_list if i in ALLOWED_COLUMNS]

    if selected_cols:
        df = df[selected_cols]
    else:
        print("Columns header are missing.")
        selected_cols = columns_list

    df['Product'] = catg

    # insert empty row at the end
    # df.loc[len(df)] = [''] * (len(selected_cols)+1)

    print(df.head(5).to_markdown(index=False))
    return df


def extract_table(page, dfs):
    """Extract tables from a single PDF page, filter by width and category."""
    tables = page.find_tables()

    for tb in tables:
        x0, y0, x1, y1 = tb.bbox

        width = abs(x1 - x0)
        # Only process tables wider than 200pt (skip narrow sidebar tables)
        if width > 200:
            table_data = tb.extract()
            # Need at least 3 rows: category header, column headers, and data
            if not table_data or len(table_data) < 3:
                print(f"Skipping table: insufficient rows ({len(table_data) if table_data else 0})")
                continue

            # Determine category from the first row of the table
            r1 = table_data[0]
            print(f"looking for table: ({round(width,2)}) row1: {r1}")

            if find_table_by_category("Men's", r1):
                catg = "Men's"
            elif find_table_by_category("Women's", r1):
                catg = "Women's"
            elif find_table_by_category("Youth", r1):
                catg = "Youth"
            else:
                catg = ""

            if catg:
                print(f"{BLUE}Category Matched: {catg}{RESET}")
                df = process_table_data(table_data, catg)
                dfs.append(df)
                print()


def process_pdf(input_path: Path, output_dir: Path, file_bytes: bytes = None) -> pd.DataFrame:
    """Main entry: extract player tables from a PDF and save as CSV.

    Args:
        input_path: Path to the PDF file (used for filename and fallback reading).
        output_dir: Directory where the output CSV will be written.
        file_bytes: Optional raw PDF bytes (used by Streamlit uploader).
    """
    dfs: List[pd.DataFrame] = []

    if file_bytes:
        print(f"{GREEN}Reading PDF from bytes: {input_path.name}{RESET}")
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
    else:
        print(f"{GREEN}Reading PDF: {input_path.name}{RESET}")
        if input_path.suffix != ".pdf":
            print(f"{RED}Skipping non-PDF file: {input_path.name}{RESET}")
            return pd.DataFrame()
        pdf = pdfplumber.open(input_path)

    print('---'*20)

    # Build output CSV path from input filename
    out_path = output_dir / input_path.name
    out_path = out_path.with_suffix('.csv')

    for i, page in enumerate(pdf.pages, start=1):
        print('=' * 40, '\n  PAGE', i, '\n', '=' * 40, sep='')
        extract_table(page, dfs)

    pdf.close()

    if dfs:
        final = pd.concat(dfs, ignore_index=True)
        final.to_csv(out_path, index=False)
        print(f"{BLUE}Saved to CSV: '{out_path}'{RESET}\n")
        return final

    else:
        print("No tables found")
        return pd.DataFrame()


def main():
    """CLI entry point: supports single file or batch processing a directory."""
    parser = argparse.ArgumentParser(
        description="Convert a PDF containing player tables into a CSV file.",
        epilog="Examples:\n"
               "  python pdf_to_csv.py players.pdf\n"
               "  python pdf_to_csv.py --all-pdfs INPUT",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "--all-pdfs",
        type=Path,
        metavar="DIR",
        help="Process all PDF files in the specified directory"
    )
    args = parser.parse_args()

    if args.all_pdfs:
        if not args.all_pdfs.is_dir():
            print(f"{RED}Error: '{args.all_pdfs}' is not a valid directory{RESET}")
            return
        folder = args.all_pdfs
        files = [p for p in folder.iterdir() if p.suffix == '.pdf']
        if not files:
            print(f"No PDF files found in '{folder}'")
            return

    elif args.input_file:
        if not args.input_file.is_file():
            print(f"Error: '{args.input_file}' is not a valid file")
            return
        files = [args.input_file]
    else:
        parser.print_help()
        return

    output_dir = Path('OUTPUT')
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_path in files:
        process_pdf(input_path=input_path, output_dir=output_dir)


if __name__ == "__main__":
    try:
        main()
    # Write unhandled exceptions to file for debugging
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        with open("error.txt", "w", encoding="utf-8") as f:
            f.write(error)

    input("Press Enter to close...")
