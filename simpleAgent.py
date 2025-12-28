from groq import Groq
import pandas as pd
import json
import os

# -------------------------------
# CONFIG
# -------------------------------
GROQ_API_KEY = "gsk_yDCBLVsLZvpw0rZ30wnPWGdyb3FYjP8HVDps1ugjEnLb6sfi_vI8"  # or use os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(api_key=GROQ_API_KEY)

# -------------------------------
# TOOLS (ACTIONS AGENT CAN TAKE)
# -------------------------------
def create_excel(file_name: str):
    """
    Tool: Creates an Excel file with the given name
    """
    df = pd.DataFrame({
        "CreatedBy": ["Jupiter Autonomous Groq Agent 🚀"]
    })
    df.to_excel(f"{file_name}.xlsx", index=False)
    return f"{file_name}.xlsx created successfully"


# Tool registry (easy to scale later)
TOOLS = {
    "create_excel": create_excel
}

# -------------------------------
# AGENT (THINK → DECIDE → ACT)
# -------------------------------
def agent(prompt: str):
    system_prompt = """
You are an autonomous AI agent.

You can use the following tools:
1. create_excel(file_name) – creates an Excel file

Your job:
- Understand the user's request completely And Decide whether a tool is needed
- If yes, select the correct tool and process the query it and Generate arguments for the tool

IMPORTANT RULES:
- Respond ONLY in valid JSON
- No explanations, no extra text

JSON FORMAT:

If tool is needed:
{
  "tool": "create_excel",
  "arguments": {
    "file_name": "<name_without_extension>"
  }
}

If no tool is needed:
{
  "tool": "none"
}

"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}    
        ],
        temperature=0
    )
 
    ai_output = response.choices[0].message.content.strip()

    print("\n🧠 AI RAW DECISION:")
    print(ai_output)

    # -------------------------------
    # PARSE AI DECISION
    # -------------------------------
    try:
        decision = json.loads(ai_output)
    except json.JSONDecodeError:
        print("❌ Invalid JSON from AI")
        return

    tool_name = decision.get("tool")

    if tool_name == "none":
        print("ℹ️ AI decided no action is needed")
        return

    if tool_name not in TOOLS:
        print(f"❌ Unknown tool: {tool_name}")
        return

    # -------------------------------
    # EXECUTE TOOL
    # -------------------------------
    tool_func = TOOLS[tool_name]
    arguments = decision.get("arguments", {})

    print("\n🛠️ AI CHOSE TOOL:", tool_name)
    print("📥 ARGUMENTS:", arguments)

    result = tool_func(**arguments)

    print("\n✅ TOOL RESULT:")
    print(result)


# -------------------------------
# RUN AGENT
# -------------------------------
if __name__ == "__main__":
    # user_prompt = "time in india current"
    user_prompt = input("Enter Your Query : ")
    agent(user_prompt)
