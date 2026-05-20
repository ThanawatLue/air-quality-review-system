import pandas as pd
import sys

def get_info(path):
    xl = pd.ExcelFile(path)
    print(f"Sheets: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        print(f"\n--- Sheet: {sheet} ---")
        print(df.head(10).to_markdown())

if __name__ == "__main__":
    get_info(sys.argv[1])
