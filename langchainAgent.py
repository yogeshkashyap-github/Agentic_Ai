# agent.py
import os
import sys
import json
import pandas as pd

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_groq import ChatGroq

# ---------- INPUT FILE ----------
if len(sys.argv) < 2:
    print("❌ Usage: python agent.py <excel_file>")
    sys.exit(1)

INPUT_FILE = sys.argv[1]

if not os.path.exists(INPUT_FILE):
    print(f"❌ File not found: {INPUT_FILE}")
    sys.exit(1)

# ---------- TOOLS ----------
def inspect_excel(file_path: str):
    df = pd.read_excel(file_path)
    return {
        "columns": list(df.columns),
        "row_count": len(df),
        "sample_rows": df.head(3).to_dict()
    }

def remove_duplicates_tool(input_data: str):
    data = json.loads(input_data)
    file_path = data["file"]
    subset = data["subset"]
    keep = data["keep"]

    df = pd.read_excel(file_path)
    before = len(df)

    cleaned_df = df.drop_duplicates(subset=subset, keep=keep)
    after = len(cleaned_df)

    cleaned_df.to_excel("output.xlsx", index=False)

    return {
        "removed_rows": before - after,
        "final_rows": after,
        "used_subset": subset,
        "keep_rule": keep
    }

tools = [
    Tool(
        name="InspectExcel",
        func=inspect_excel,
        description="Inspect Excel file to understand columns and sample data"
    ),
    Tool(
        name="RemoveDuplicates",
        func=remove_duplicates_tool,
        description="""
        Remove duplicate rows from Excel.
        Input JSON: { "file": "<excel_file>", "subset": [...], "keep": "first/last" }
        """
    )
]

# ---------- LLM ----------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ---------- PULL PROMPT TEMPLATE FROM HUB ----------
react_prompt = hub.pull("hwchase17/react")

# ---------- CREATE AGENT ----------
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---------- RUN AGENT ----------
agent_executor.invoke({
    "input": f"Autonomously dedupe Excel file: {INPUT_FILE}"
})
