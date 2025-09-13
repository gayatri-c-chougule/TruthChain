import streamlit as st  

# === Streamlit Configuration ===
# This file defines the "Know More" / About page of the Truth Chain app.
# It uses Streamlit to render a structured markdown description of how the system works.
# Updated: focuses on multi-source tools first, positions LangGraph as the orchestrator,
# and adds a short tagline + evaluation snapshot for portfolio clarity.

# Page title and layout
st.set_page_config(page_title="Know More – Truth Chain", layout="wide")

# === About Section Header ===
st.markdown("## 📘 Know More: About *Truth Chain – AI Claim Analyzer*")
st.markdown("**Multi-tool claim verification powered by AI — Google, PubMed, Arxiv, Wikipedia, Tavily — orchestrated with LangGraph.**")

# === Informational Content ===
# Overview of the project, architecture, technical stack, and use cases
st.markdown(
    """
---
### 🔍 What does it do?

**Truth Chain** is an intelligent claim verification assistant that analyzes any factual statement you enter — and classifies it as **True**, **False**, or **Unverifiable**.  

It queries a **diverse set of online knowledge tools** — Google, PubMed, Wikipedia, Arxiv, and Tavily — and fuses their results into a single verdict with clear reasoning and transparent sources.  
Covers **general knowledge, science, medicine, history, and news** using specialized tools.

---

### ⚙️ How does it work?

This app uses **LangGraph** as the orchestration layer to manage a modular AI reasoning flow.  

1. **Tool Selection (Router Node)**  
   - An LLM classifier decides which tools (Google, PubMed, etc.) are most relevant to the claim.  
   - Example mapping:  
     - Google → general fact-checking  
     - PubMed → health/medical facts  
     - Arxiv → research-level science  
     - Wikipedia → historic/general knowledge  
     - Tavily → current news/events  

2. **Tool Execution**  
   - The chosen tools are invoked to gather contextual evidence (search results, abstracts, summaries).  

3. **Focused Summarization**  
   - Each tool’s raw output is compressed **in relation to the claim**, discarding irrelevant details.  

4. **Final Verdict**  
   - An LLM reviews the evidence and outputs: ✅ True / ❌ False / 🤷‍♂️ Unverifiable  
   - Includes a short **reasoning string** explaining *why*.  

5. **Evaluation Engine**  
   - An automated script runs test claims from CSV, compares against ground truth, and logs metrics for accuracy tracking.  

---
"""
)

#  evaluation snapshot to demonstrate real results without overwhelming the page
st.markdown(
    """
- 32 claims tested on **2025-09-11**  
- **GPT-4o** → Accuracy: **87.5% (28 / 32 correct)**  
- **GPT-4o-mini** → Accuracy: **84.38% (27 / 32 correct)**  

📌 *For hosting, GPT-4o-mini is used to lower cost and latency, while still maintaining strong accuracy.  
For maximum accuracy (e.g., production-critical use), the pipeline can switch to GPT-4o.*
"""
)

# Collapse the Tech Stack so the page stays compact
with st.expander("🧠 Tech Stack (click to expand)"):
    st.markdown(
        """
| Layer                | Technology                                        |
|----------------------|---------------------------------------------------|
| 🔎 Evidence Tools     | Google (Serper), PubMed, Arxiv, Wikipedia, Tavily |
| 💬 LLM Engine         | OpenAI GPT-4o (via LangChain)                     |
| 🧩 Orchestration      | LangGraph nodes & state graph                      |
| 🧪 Summarization      | PromptTemplate + focused summarizer logic         |
| 📊 Evaluation         | CSV batch evaluation + metrics logger             |
| 🌐 UI                 | Streamlit with expandable tool outputs            |
| 📁 Config             | `.env` secrets, env-driven model & file paths     |
"""
    )

# Sample use cases remain visible (helpful to readers deciding what to try)
st.markdown(
    """
---
### 🧪 Sample Use Cases

- **Fact-checking** political or scientific claims  
- **Verifying medical advice** with PubMed literature  
- **Checking recent news events** using Tavily or Google  
- **Academic hypothesis vetting** with Arxiv papers  
"""
)
