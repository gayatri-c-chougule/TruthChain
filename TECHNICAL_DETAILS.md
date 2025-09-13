# 🔬 Technical Details — Truth Chain

This document captures the **implementation details** of Truth Chain that are separated from the main README for clarity.  
It explains how claims are processed, how tools are orchestrated, and how evaluation is performed.  

---

## 🛠 Tool Integrations
Truth Chain uses modular tool wrappers located in the `Tools/` directory:

- **Google Search** — Serper API (`google_search.py`)  
- **PubMed** — NCBI E-utilities API (`pubmed_tool.py`)  
- **Arxiv** — Arxiv API + PyMuPDF (for summaries) (`arxiv_tool.py`)  
- **Wikipedia** — Python `wikipedia` library (`wikipedia_search.py`)  
- **Tavily** — Tavily Search API (`tavily_search.py`)  

👉 Each tool retrieves raw evidence (snippets, abstracts, or full articles).  
👉 Evidence is **summarized relative to the claim** using helper functions in `utils.py`.  

---

## 📄 Summarization Logic
- Located in `utils.py` (`summarize_article_with_focus`).  
- **Fetcher:** `trafilatura` — extracts the main content from article URLs.  
- **Process:**  
  1. Limit article size with a safeguard (`max_chars=4000`).  
  2. Pass the article + user claim into a focused LLM prompt.  
  3. Generate 2–3 paragraphs highlighting only content **relevant to the claim**.  

This ensures Truth Chain bases verdicts on **article-level context**, not just shallow snippets.  

---

## 🤖 Router & Verdict Nodes
- **Router Node** (`LangGraph.py`)  
  - Implemented as `decide_tools_node`.  
  - Uses an LLM prompt to **categorize the claim** and return a Python list of relevant tools.  
  - Special handling for **Tavily** if the claim contains recency markers (*“today,” “last week,” “recently”*).  
  - Fallback: defaults to `['Google']` if classification fails.  

- **Verdict Node**  
  - Collects all **focused summaries** from the selected tools.  
  - LLM outputs a structured verdict:  
    - ✅ `True`  
    - ❌ `False`  
    - 🤷 `Unverifiable`  
  - Includes a concise reasoning string alongside the verdict.  

---

## 🏗 Orchestration
Truth Chain uses **LangGraph** to model the reasoning flow as a modular state graph:

1. **Router Node** → decide relevant tools.  
2. **Tool Nodes** → query APIs and fetch evidence.  
3. **Summarizers** → condense evidence relative to the claim.  
4. **Verdict Node** → aggregate summaries and produce the final verdict.  

This modular design makes it easy to add or swap tools without breaking the pipeline.  

---

## 📊 Evaluation
- **Script:** `evaluate.py`  
- **Dataset:** 32 claims with ground-truth labels.  
- **Models tested:**  
  - GPT-4o → **87.5% (28/32 correct)**  
  - GPT-4o-mini → **84.38% (27/32 correct)**  
- **Flow:**  
  1. Load claims from CSV (`claim,ground_truth`).  
  2. Route → Tools → Summaries → Verdict.  
  3. Compare verdict with ground truth.  
  4. Log metrics to CSV and display results in the README’s evaluation table.  

---

## 🏗 Deployment
- Hosted live on **AWS EC2**.  
- Dependencies installed **globally** (not inside a virtual environment).  
- Run via `nohup` to keep the app alive after SSH logout:  
  ```bash
  nohup streamlit run Main.py --server.port 8502 --server.address 0.0.0.0 > truthchain.log 2>&1 &
