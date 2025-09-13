# wikipedia_search.py

import wikipedia
from utils import summarize_article_with_focus  # Handles focused summarization

def wikipedia_summary(query: str, fallback_sentences: int = 16, max_chars: int = 75000) -> str:
    """
    Search Wikipedia and return a focused summary of the top result.

    If the full page content is under a character limit, use it to generate
    a claim-focused summary. Otherwise, fall back to a short general summary.

    Args:
        query (str): The search term or user claim to analyze.
        fallback_sentences (int): Number of sentences in fallback mode.
        max_chars (int): Max characters to consider from full article for LLM summarization.

    Returns:
        str: Formatted Markdown summary with source and focus-based summary.
    """
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return f"❌ No Wikipedia results for: {query}" 

        # Use the first search result
        page_title = search_results[0]
        page = wikipedia.page(page_title, auto_suggest=False)
        full_content = page.content.strip()
        url = page.url

        # Use full article if it's within length limits
        if len(full_content) < max_chars and query:
            focused = summarize_article_with_focus(full_content[:max_chars], focus=query)
            summary = f"{focused}\n\n📌 Article excerpt from Wikipedia"
        else:
            # Fallback to a generic summary if the article is too long
            brief = wikipedia.summary(page_title, sentences=fallback_sentences)
            summary = f"(Fallback summary: {fallback_sentences} sentences)\n\n{brief}"

        return (
            f"**{page.title}** — _Wikipedia_\n"
            f"🔗 [Full Article]({url})\n\n"
            f"🔎 **Focused Summary:**\n{summary.strip()}\n"
        )

    except Exception as e:
        return f"❌ Wikipedia error for '{query}': {e}"


# Example usage (for module-level testing)
# def test_wikipedia_summary():
#     print("\n🔍 Test 1: Standard topic")
#     result = wikipedia_summary("NASA moon landing")
#     print(result)

# if __name__ == "__main__":
#     test_wikipedia_summary()
