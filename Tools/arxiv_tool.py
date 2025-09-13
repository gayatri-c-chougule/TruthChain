import arxiv
import fitz  # PyMuPDF
import tempfile
import requests
from datetime import datetime
from utils import summarize_article_with_focus
import tiktoken  


# === Token Counter ===
def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count the number of tokens in the given text using the tokenizer for the specified model.
    Useful for managing LLM input limits.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text or ""))


# === Section Extractor ===
def extract_focus_sections(full_text: str) -> str:
    """
    Extract key sections (Introduction, Conclusion) from a long research paper
    to reduce token usage while retaining essential information.
    """
    lower = full_text.lower()
    sections = []

    def get_section(start_keywords, end_keywords=None):
        for start_kw in start_keywords:
            start_idx = lower.find(start_kw)
            if start_idx != -1:
                if end_keywords:
                    for end_kw in end_keywords:
                        end_idx = lower.find(end_kw, start_idx + 1)
                        if end_idx != -1:
                            return full_text[start_idx:end_idx]
                # fallback: extract a chunk if no proper end found
                return full_text[start_idx:start_idx + 3000]
        return ""

    # Try to extract intro and conclusion (skip unrelated parts)
    intro = get_section(
        ["introduction"],
        ["related work", "background", "method", "methods"]
    )
    conclusion = get_section(
        ["conclusion", "discussion", "summary"],
        ["acknowledgements", "references", "bibliography"]
    )

    return intro + "\n\n" + conclusion


# === PDF Downloader & Extractor ===
def download_arxiv_pdf(pdf_url: str) -> str:
    """
    Downloads the PDF from ArXiv and extracts full text using PyMuPDF.
    Returns the full text as string.
    """
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)
        full_text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return full_text.strip()

    except Exception as e:
        return f"❌ Error downloading or extracting PDF: {e}"


# === ArXiv Summarizer Tool ===
def arxiv_summary(query: str, focus: str, max_results: int = 1) -> str:
    """
    Search ArXiv for a given query and return a focused summary based on the full paper content.
    Falls back to abstract if full text cannot be extracted.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = list(search.results())

        if not results:
            return f"❌ No ArXiv results for: {query}"

        top = results[0]
        title = top.title.strip().replace('\n', ' ')
        authors = ", ".join([a.name for a in top.authors])
        abstract = top.summary.strip().replace('\n', ' ')
        url = top.entry_id
        date = top.published.strftime('%Y-%m-%d')
        pdf_url = top.pdf_url

        # === Download full paper and summarize ===
        full_text = download_arxiv_pdf(pdf_url)

        if full_text.startswith("❌"):
            summary = f"(Fallback to abstract)\n\n{abstract}"
        else:
            token_count = count_tokens(full_text)
            if token_count > 10000:
                # Extract only intro/conclusion if paper is too long
                focus_text = extract_focus_sections(full_text)
                summary = summarize_article_with_focus(focus_text, focus=focus)
            else:
                summary = summarize_article_with_focus(full_text, focus=focus)

        return (
            f"**Title**: {title}\n"
            f"**Authors**: {authors}\n"
            f"**Published**: {date}\n"
            f"**URL**: {url}\n"
            f"**PDF**: {pdf_url}\n\n"
            f"🧾 **Summary (focused on):** _{focus}_\n\n{summary}"
        )

    except Exception as e:
        return f"❌ ArXiv error for '{query}': {e}"


# === Example Usage ===
# Uncomment for standalone testing of this module.
# if __name__ == "__main__":
#     query = "GPT-4 architecture"
#     focus = "GPT-4 uses a mixture-of-experts architecture"
#     result = arxiv_summary(query, focus)
#     print(result)
