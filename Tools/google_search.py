import os
import requests
from dotenv import load_dotenv
from utils import get_article, summarize_article_with_focus  

# Load environment variables from .env (e.g., SERPER_API_KEY)
load_dotenv()


# === Google Search Tool ===
def google_search(query: str) -> str:
    """
    Performs a Google search using Serper.dev API and returns summarized results.
    
    For each top 2 results:
    - Fetches the full article
    - Performs focused summarization relevant to the query
    - Returns the title, snippet, summary, and link
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "❌ SERPER_API_KEY not found in environment."

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Get top 2 organic search results
        results = data.get("organic", [])[:2]
        if not results:
            return "No results found."

        output = ""

        # Process each search result
        for i, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No snippet")
            link = result.get("link", "")
            summary = ""

            # Try extracting and summarizing full article
            if link:
                full_article = get_article(link)

                if full_article and not full_article.startswith("❌"):
                    summary = summarize_article_with_focus(full_article, focus=query)
                    summary = f"🔎 **Focused Summary:**\n{summary}\n"
                else:
                    summary = "🔍 Could not extract article."

            output += f"**{i}. {title}**\n{snippet}\n{summary}\n[{link}]({link})\n\n"

        return output.strip()

    except Exception as e:
        return f"❌ Error fetching Google results: {e}"


# === Example Usage ===
# Uncomment to test module directly
# if __name__ == "__main__":
#     test_query = "What are people saying about the 2024 US election debates?"
#     print("🔍 Searching Google for:", test_query)
#     result = google_search(test_query)
#     print("\n🧾 Result:\n", result)
