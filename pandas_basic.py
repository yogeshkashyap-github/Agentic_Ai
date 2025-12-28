import pandas as pd
# ---------- TOOLS ----------


# ---------- TOOLS ----------
def inspect_excel(file_path: str):
    sheets = pd.read_excel(file_path,sheet_name=None)
    print(sheets)

    for sheet_name, df in sheets.items():
        print(f"Processing sheet: {sheet_name}")
        print(df.head(5).to_dict())

    # return {
    #     "columns": list(df.columns),
    #     "row_count": len(df),
    #     "sample_rows": df.head(1).to_dict()
    # }

print(inspect_excel("input.xlsx"))