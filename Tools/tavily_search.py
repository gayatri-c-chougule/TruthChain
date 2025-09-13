# === Imports and Environment Setup ===
import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("TAVILY_API_KEY")


# === Main Tavily Search Tool ===
def tavily_search(query: str, max_results: int = 4) -> str:
    """
    Performs a Tavily search using the provided query string.
    
    Parameters:
        query (str): The search question or statement (e.g., "Biden approval rating 2024")
        max_results (int): Number of search results to return (default = 4)

    Returns:
        str: Formatted markdown-like summary of Tavily results, or error message.
    """
    if not API_KEY:
        return "❌ TAVILY_API_KEY missing in .env"

    # Initialize the TavilySearch tool (LangChain wrapper for Tavily API)
    tool = TavilySearch(
        api_key=API_KEY,
        max_results=max_results,
        include_answer=True,        # include LLM-generated answer (not used here)
        include_raw_content=True,   # include raw snippet/article content
        include_images=False        # skip images to save bandwidth
    )

    try:
        # Perform search via LangChain interface
        results = tool.invoke({"query": query})

        # If result is wrapped inside a dictionary, extract the actual list
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        if not results:
            return "No Tavily results."

        # Format the search results into readable numbered list
        lines = []
        for i, r in enumerate(results, 1):
            title = (r.get("title") or "No title").strip()
            content = (r.get("content") or "").strip()
            url = r.get("url") or ""  

            lines.append(f"**{i}. {title}**\n{content}\n[{url}]({url})\n")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Tavily search failed: {e}"


# === Module-level test block ===
# if __name__ == "__main__":
#     print(tavily_search("The Eiffel Tower in Paris was closed in January 2025 due to worker strikes."))
