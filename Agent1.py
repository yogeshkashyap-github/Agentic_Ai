import pandas as pd
from groq import Groq
import json


def summarize_excel(df):
    return {
        "columns": list(df.columns),
        "rows": len(df),
        "sample": df.head(3).to_dict()
    }



def remove_duplicates(df, subset, keep):
    return df.drop_duplicates(subset=subset, keep=keep)



def validate(old_df, new_df):
    return {
        "before": len(old_df),
        "after": len(new_df)
    }

def data_merger(df1,df2,on,how):
    return pd.merge(df1,df2,how=how,on=on)

def agent_decide(user_query,excel_summary,sheet_naam):


    SYSTEM_PROMPT = """
    Your goal:
    Process user query and decide subset and keep for removing duplicate records from Excel data whose summary will be provided.

    Rules:
    - Do NOT assume column names
    - Give valid Json donot give any detail not even ```json or ```

    Sample Output As JSON
    { subset : <suitable subset as per user query>,
        keep : <keep>
    }
    """

    client = Groq(api_key="gsk_yDCBLVsLZvpw0rZ30wnPWGdyb3FYjP8HVDps1ugjEnLb6sfi_vI8")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"SheetName : {sheet_naam} | Excel summary: {excel_summary} User Query : {user_query} "}
        ]
    )

    decision = response.choices[0].message.content.replace("```json","").replace("```","")

    print(decision)

    return decision


# --------------------------------------------------------------------------

sheets = pd.read_excel("input.xlsx",sheet_name=None)
# print(sheets)

for sheet_name, df in sheets.items():
    summary = summarize_excel(df)


    user_query = "Kindly remove the duplicated acc to the dept"
    decision = agent_decide(user_query,summary,sheet_name)


    rules = json.loads(decision)    

    clean_df = remove_duplicates(
        df,
        subset=rules["subset"],
        keep=rules["keep"]
    )

    print(clean_df)

    # print(validate(df, clean_df))

    # clean_df.to_excel("output.xlsx", index=False)

    print("\n\n\n")

 