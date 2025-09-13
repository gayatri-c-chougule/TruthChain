# claim_verification_graph.py

# --- Imports ---
from typing import List, Optional, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Tool imports
from Tools.google_search import google_search
from Tools.arxiv_tool import arxiv_summary
from Tools.pubmed_tool import pubmed_search
from Tools.tavily_search import tavily_search
from Tools.wikipedia_search import wikipedia_summary

# Load API keys
load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0)

# --- Graph State Definition ---
class GraphState(TypedDict):
    """Shared state structure passed between LangGraph nodes."""
    user_input: str
    selected_tools: Optional[List[str]]
    tool_outputs: Optional[dict]
    final_verdict: Optional[str]


# --- Tool Selection Node ---
def decide_tools_node(input: GraphState) -> GraphState:
    """
    Uses LLM to select appropriate tools for the given claim.

    - Takes user_input from GraphState
    - Sends system prompt to LLM with classification task
    - Returns selected_tools list (e.g., ["Google", "PubMed"])
    """
    user_claim = input.get("user_input", "")

    system_prompt = """
You are a smart classifier. Given a user's information or claim, identify which sources/tools are best to verify it.
Available tools:
- Google 
- PubMed 
- Wikipedia 
- Tavily search 
- Arxiv

Return a Python list of tool names most relevant for verifying the information.
Only return tool names. Do not include explanation.
If unsure, return ['Google'] as fallback.
"""

    response = llm.invoke([
        HumanMessage(content=system_prompt.strip()),
        HumanMessage(content=user_claim)
    ])

    import ast
    try:
        tools = ast.literal_eval(response.content.strip())
        assert isinstance(tools, list)
    except Exception:
        tools = ["Google"]  # Fallback if parsing fails

    return {
        "user_input": user_claim,
        "selected_tools": tools
    }


# --- Individual Tool Nodes ---
def google_node(state: GraphState) -> GraphState:
    """
    Runs Google search for the claim and updates tool_outputs.
    """
    query = state["user_input"]
    result = google_search(query)

    prev_outputs = state.get("tool_outputs", {})
    updated_outputs = {**prev_outputs, "Google": result}
    return {**state, "tool_outputs": updated_outputs}


def pubmed_node(state: GraphState) -> GraphState:
    """
    Runs PubMed search for the claim and updates tool_outputs.
    """
    query = state["user_input"]
    result = pubmed_search(query, query)

    prev_outputs = state.get("tool_outputs", {})
    updated_outputs = {**prev_outputs, "PubMed": result}
    return {**state, "tool_outputs": updated_outputs}


def tavily_node(state: GraphState) -> GraphState:
    """
    Runs Tavily search for the claim and updates tool_outputs.
    """
    query = state["user_input"]
    result = tavily_search(query)

    prev_outputs = state.get("tool_outputs", {})
    updated_outputs = {**prev_outputs, "Tavily": result}
    return {**state, "tool_outputs": updated_outputs}


def wikipedia_node(state: GraphState) -> GraphState:
    """
    Runs Wikipedia search for the claim and updates tool_outputs.
    """
    query = state["user_input"]
    result = wikipedia_summary(query)

    prev_outputs = state.get("tool_outputs", {})
    updated_outputs = {**prev_outputs, "Wikipedia": result}
    return {**state, "tool_outputs": updated_outputs}


def arxiv_node(state: GraphState) -> GraphState:
    """
    Runs Arxiv search for the claim and updates tool_outputs.
    """
    query = state["user_input"]
    result = arxiv_summary(query, query)

    prev_outputs = state.get("tool_outputs", {})
    updated_outputs = {**prev_outputs, "Arxiv": result}
    return {**state, "tool_outputs": updated_outputs}


# --- Tool Dispatcher Node ---
def run_selected_tools(state: GraphState) -> GraphState:
    """
    Dispatches execution of tools selected in the previous node.

    Returns updated state with tool_outputs populated from tools.
    """
    tools = state.get("selected_tools", [])
    merged_output = {}

    for tool in tools:
        if tool == "Google":
            result = google_node(state)
        elif tool == "PubMed":
            result = pubmed_node(state)
        elif tool == "Tavily search":
            result = tavily_node(state)
        elif tool == "Wikipedia":
            result = wikipedia_node(state)
        elif tool == "Arxiv":
            result = arxiv_node(state)
        else:
            continue  # Skip unknown tools

        merged_output.update(result.get("tool_outputs", {}))

    return {
        "user_input": state["user_input"],
        "selected_tools": tools,
        "tool_outputs": merged_output
    }


# --- Final Verdict Node ---
def evaluate_claim_node(state: GraphState) -> GraphState:
    """
    Uses an LLM to evaluate the claim based on tool_outputs.

    Returns final_verdict in the format:
    Verdict: [True / False / Unverifiable]
    Reason: <summary>
    """
    claim = state["user_input"]
    tool_outputs = state.get("tool_outputs", {})

    # Format context for LLM
    context_text = "\n\n".join(
        [f"🔎 Source: {tool}\n{output}" for tool, output in tool_outputs.items()]
    )

    system_prompt = """
You are a fact verification assistant. Given a claim and search results from various sources (Google, PubMed, Wikipedia, etc.), determine whether the claim is:

- ✅ TRUE: Clearly supported by the evidence
- ❌ FALSE: Clearly contradicted by the evidence
- 🤔 UNVERIFIABLE: Not clearly confirmed or denied by the evidence

Only use the provided context. Do not guess. Always explain your reasoning.

Format your answer as:

Verdict: [True / False / Unverifiable]
Reason: <short explanation based only on context>
"""

    user_message = f"Claim: {claim}\n\nContext:\n{context_text}"

    response = llm.invoke([
        HumanMessage(content=system_prompt.strip()),
        HumanMessage(content=user_message.strip())
    ])

    return {**state, "final_verdict": response.content.strip()}


# --- LangGraph Assembly ---
from langgraph.graph import StateGraph, END

builder = StateGraph(GraphState)
builder.add_node("DecideTools", decide_tools_node)
builder.add_node("RunTools", run_selected_tools)
builder.add_node("EvaluateClaim", evaluate_claim_node)

builder.set_entry_point("DecideTools")
builder.add_edge("DecideTools", "RunTools")
builder.add_edge("RunTools", "EvaluateClaim")
builder.add_edge("EvaluateClaim", END)

graph = builder.compile()


# --- Graph Entry Point (for use in app.py or Streamlit frontend) ---
def get_remedy_graph():
    """
    Returns compiled LangGraph object for external invocation.
    """
    return graph


#--- Module-level Testing ---
# if __name__ == "__main__":
#     user_input = "ChatGPT passed the bar exam in the US."
#     final_state = graph.invoke({"user_input": user_input})
#     print("🧪 Final State:")
#     print("Selected tools:", final_state.get("selected_tools"))
#     print("Tool outputs:", final_state.get("tool_outputs", {}).keys())
#     print("\n📣 Verdict:\n", final_state.get("final_verdict"))
