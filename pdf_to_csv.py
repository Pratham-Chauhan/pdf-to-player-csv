import traceback
from typing import List

import pdfplumber
import pandas as pd
from pathlib import Path
import argparse


pdf = None
find_table_by_category = (lambda cat, row: any([cat in x.strip() for x in row if x]))

def read_input(input_file: Path):
    print('Reading PDF:', input_file.name)
    print('---'*20)
    pdf = pdfplumber.open(input_file)

    return pdf 


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
    df.loc[len(df)] = [''] * (len(selected_cols)+1)

    print(df.to_string(index=False))

    return df


def extract_table(page, dfs, output_path):
    tables = page.find_tables()
    

    for tb in tables:
        x0, y0, x1, y1 = tb.bbox

        width = abs(x1 - x0)
        if width > 200:

            table_data = tb.extract()
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
                print('Category Matched:', catg)
                df = process_table_data(table_data, catg)
                dfs.append(df)
                # print()
    #
    if dfs:
        final = pd.concat(dfs)
        final.to_csv(output_path, index=False)
        print(f"Saved to CSV: '{output_path.name}'")
    else:
        print("No tables found")

def main():
    global pdf

    parser = argparse.ArgumentParser(
        description="Convert a PDF containing player tables into a CSV file.",
        epilog="Example: python pdf_to_csv.py players.pdf"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input PDF file"
    )
    args = parser.parse_args()

    dfs: List[pd.DataFrame] = []

    pdf = read_input(args.input_file)
    output_path = args.input_file.with_suffix(".csv")
    
    for page in pdf.pages:
        extract_table(page, dfs, output_path)




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
