import pandas as pd
import sys

def dump_excel(path):
    # Try reading with openpyxl
    df = pd.read_excel(path, sheet_name=0)
    # Set display options to see more
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 100)
    print(df.to_markdown())

if __name__ == "__main__":
    dump_excel(sys.argv[1])
