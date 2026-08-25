import os
import traceback
from typing import List

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


pdf = None
find_table_by_category = (lambda catg, row: any([catg in x.strip() for x in row if x]))



def process_table_data(tdata, catg) -> pd.DataFrame:

    df = pd.DataFrame(tdata[2:], columns=tdata[1])

    columns_list = df.columns.to_list()
    ALLOWED_COLUMNS = ['Size', '#', 'Names']
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


def extract_table(page, dfs, output_path):
    tables = page.find_tables()
    
    for tb in tables:
        x0, y0, x1, y1 = tb.bbox

        width = abs(x1 - x0)
        if width > 200:

            table_data = tb.extract()
            if not table_data or len(table_data) < 3:
                print(f"Skipping table: insufficient rows ({len(table_data) if table_data else 0})")
                continue

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

            
def read_input(input_file: Path):
    print(f"{GREEN}Reading PDF: {input_file.name}{RESET}")
    print('---'*20)
    pdf = pdfplumber.open(input_file)

    return pdf 

def main():
    global pdf

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
        dfs: List[pd.DataFrame] = []
        pdf = read_input(input_path)

        if input_path.suffix == '.pdf':
            out_path = output_dir / input_path.name
            out_path = out_path.with_suffix('.csv')

            for i, page in enumerate(pdf.pages, start=1):
                print('=' * 40)
                print(f'  PAGE {i}')
                print('=' * 40)
                extract_table(page, dfs, out_path)
                
            #
            if dfs:
                final = pd.concat(dfs)
                final.to_csv(out_path, index=False)
                print(f"{BLUE}Saved to CSV: '{out_path}'{RESET}\n")
            else:
                print("No tables found")



if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        error = traceback.format_exc()
        print(error)
        with open("error.txt", "w", encoding="utf-8") as f:
            f.write(error)

    finally:
        if pdf: 
            pdf.close()

    input("Press Enter to close...")
