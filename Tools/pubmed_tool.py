import os
import requests  
from dotenv import load_dotenv
from Bio import Entrez
from utils import get_article, summarize_article_with_focus  

# === Load environment variables and configure Entrez ===
# Required for PubMed API usage (email is mandatory per NCBI policy)
load_dotenv()
EMAIL = os.getenv("NCBI_EMAIL") 
Entrez.email = EMAIL


# === Utility: Convert PubMed ID to its webpage URL ===
def _pmid_to_url(pmid: str) -> str:
    """
    Constructs a clickable PubMed URL from a given PMID.
    """
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


# === Main PubMed Search Tool ===
def pubmed_search(query: str, focus: str = "", max_results: int = 2) -> str:
    """
    Searches PubMed for the given query, fetches top results, and summarizes them.
    
    Parameters:
        query (str): The search term (e.g., "mRNA vaccine fertility")
        focus (str): The user's original claim, used to focus summarization
        max_results (int): Number of PubMed articles to fetch (default: 2)
    
    Returns:
        str: Markdown-formatted summary of search results (title, journal, date, summary, links)
    """
    try:
        # Step 1: Perform search
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        record = Entrez.read(handle)
        handle.close()

        id_list = record.get("IdList", [])
        if not id_list:
            return "No PubMed results."

        # Step 2: Fetch metadata for matched articles
        handle = Entrez.efetch(db="pubmed", id=",".join(id_list), retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        lines = []

        # Step 3: Process each article
        for article in records.get("PubmedArticle", []):
            citation = article["MedlineCitation"]
            article_data = citation.get("Article", {})

            # Extract core metadata
            pmid = citation.get("PMID", "?")
            title = article_data.get("ArticleTitle", "No title")
            abstract = article_data.get("Abstract", {}).get("AbstractText", [""])[0]
            journal = citation.get("MedlineJournalInfo", {}).get("MedlineTA", "Unknown journal")
            year = citation.get("ArticleDate", [{}])[0].get("Year", "n.d.")
            url = _pmid_to_url(str(pmid))

            # Step 4: Try to find DOI to build full-text URL
            full_url = None
            ids = article.get("PubmedData", {}).get("ArticleIdList", [])
            for item in ids:
                if item.attributes.get("IdType") == "doi":
                    full_url = f"https://doi.org/{item}"
                    break

            # Step 5: Try extracting & summarizing full-text if available
            summary = ""
            if full_url:
                full_text = get_article(full_url)

                if full_text and len(full_text) > 1000 and focus:
                    # Focused summarization from full-text + abstract backup
                    summary = summarize_article_with_focus(full_text[:75000], focus)
                    summary += f"\n\n📌 Abstract (for reference):\n{abstract}"
                elif abstract:
                    summary = f"(Fallback to abstract)\n\n{abstract}"
                else:
                    summary = "No summary available."
            else:
                # Use abstract if full-text link not available
                summary = abstract or "No summary available."

            # Step 6: Format the result
            lines.append(
                f"**{title}** — _{journal} ({year})_\n"
                f"🔗 [PubMed]({url}) {' | [Full Text](' + full_url + ')' if full_url else ''}\n\n"
                f"🔎 **Focused Summary:**\n{summary.strip()}\n"
            )

        return "\n\n".join(lines)

    except Exception as e:
        return f"❌ PubMed error: {e}"


# === Module-level test block ===
# if __name__ == "__main__":
#     query = "Vaccination is bad"
#     print(pubmed_search(query, focus=query))
