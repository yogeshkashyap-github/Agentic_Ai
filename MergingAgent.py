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



def agent_decide(user_query,df1_summary,df2_summary,sheet_name):

    SYSTEM_PROMPT = """
    Your goal:
    Process user query and decide how and on for merging dataframes whose summary will be provided.

    Rules:
    - Do NOT assume column names
    - Give valid Json donot give any detail not even ```json or ```

    Sample Output As JSON
    { how : <As per User Query>,
        on : <Best Column as on>,
        message : <Short Reply and Reason>
    }
    """

    client = Groq(api_key="gsk_yDCBLVsLZvpw0rZ30wnPWGdyb3FYjP8HVDps1ugjEnLb6sfi_vI8")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"left_dataframe Summary: {df1_summary} | right_dataframe Summary : {df2_summary} |  User Query : {user_query} "}
        ]
    )

    decision = response.choices[0].message.content.replace("```json","").replace("```","")

    print("\n",decision,"\n\n")

    return decision


# --------------------------------------------------------------------------
super_df = pd.DataFrame()

sheets = pd.read_excel("merge.xlsx",sheet_name=None)
# print(sheets)

sheetnumber = 0

for sheet_name, df in sheets.items():

    if(sheetnumber == 0):
        super_df = df.copy()
        sheetnumber+=1
        continue
    

    summary1 = summarize_excel(super_df)
    summary2 = summarize_excel(df)


    user_query = "Merge both "
    
    decision = agent_decide(user_query,summary1,summary2,sheet_name)


    rules = json.loads(decision)    

    joint = data_merger(super_df,df,rules["on"],str(rules["how"]))

    print(joint)

    super_df = joint

    print("\n\n\n")


super_df.to_excel("merged.xlsx",index=False)
 