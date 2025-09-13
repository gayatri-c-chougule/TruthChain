# Main.py

import streamlit as st
from LangGraph import graph  # Import compiled LangGraph
from typing import Dict

# --- Page Config ---
st.set_page_config(page_title="Truth Chain", layout="wide")  # Full-width layout for better readability

# --- App Title and Description ---
st.markdown("## 🧠 Truth Chain: AI Claim Analyzer with Multi-Source Tools")
st.markdown("##### Multi-tool powered: Google, Wikipedia, PubMed, Arxiv, Tavily")

# --- Instruction Header ---
st.markdown("""
### 🔍 Claim Verification Tool  
Enter a factual claim below and check if it is **True**, **False**, or **Unverifiable**.
""")

# --- User Input Section ---
user_claim = st.text_input("💬 Enter your claim here:", placeholder="e.g. ChatGPT passed the bar exam")

# --- On Verify Button Click ---
if st.button("🔎 Verify Claim"):
    if user_claim.strip():
        # Show loading spinner while verification runs
        with st.spinner("Verifying..."):
            # Run the LangGraph pipeline with user input
            final_state: Dict = graph.invoke({"user_input": user_claim.strip()})

        # --- Verdict Display ---
        verdict = final_state.get("final_verdict", "No verdict available.")
        st.subheader("📣 Verdict")
        st.success(verdict if "✅" in verdict else verdict)  # Display verdict with ✅ or ❌ as visual cue

        # --- Selected Tools Display ---
        st.subheader("🔧 Tools Used")
        st.write(", ".join(final_state.get("selected_tools", [])))

        # --- Source Outputs (Expandable by Tool) ---
        st.subheader("📚 Source Outputs")
        tool_outputs = final_state.get("tool_outputs", {})
        for tool, output in tool_outputs.items():
            with st.expander(f"{tool} Output"):
                st.markdown(output)
    else:
        st.warning("⚠️ Please enter a claim before clicking verify.")


# --- Sample Claims for User Reference ---
with st.expander("💡 Try Sample Claims (with Verdicts & Reasoning)"):
    samples = [
        {
            "claim": "ChatGPT passed the bar exam in the US.",
            "verdict": "✅ Verdict: True",
            "reason": "GPT-4 successfully passed the Uniform Bar Examination in the US, achieving a score above the passing threshold and ranking in the 90th percentile.",
            "tools": "Google"
        },
        {
            "claim": "GPT-4 can generate working Python code.",
            "verdict": "✅ Verdict: True",
            "reason": "Multiple sources, including Google and Arxiv papers, confirm GPT-4’s ability to generate and debug Python code, especially for data visualization and programming tasks.",
            "tools": "Google, Arxiv"
        },
        {
            "claim": "COVID-19 vaccines cause infertility.",
            "verdict": "❌ Verdict: False",
            "reason": "A systematic review and PubMed studies show no significant impact of COVID-19 vaccines on fertility. Major medical bodies confirm infertility is scientifically unlikely.",
            "tools": "Google, PubMed"
        },
        {
            "claim": "mRNA vaccines were first used during COVID-19.",
            "verdict": "✅ Verdict: True",
            "reason": "PubMed, Google, and Wikipedia confirm that while mRNA technology was under development for years, the first widespread use was during the COVID-19 pandemic with Pfizer/Moderna vaccines.",
            "tools": "PubMed, Google, Wikipedia"
        },
        {
            "claim": "NASA faked the moon landing.",
            "verdict": "❌ Verdict: False",
            "reason": "Both Google and Wikipedia debunk moon-landing conspiracy theories, citing third-party evidence like Lunar Reconnaissance Orbiter photos and scientific consensus dismissing the hoax claims.",
            "tools": "Google, Wikipedia"
        }
    ]

    # Loop through each sample and render nicely
    for s in samples:
        st.markdown(f"#### {s['claim']}")
        st.markdown(f"**{s['verdict']}**")
        st.markdown(f"**Reason:** {s['reason']}")
        st.markdown(f"**Tools Used:** {s['tools']}")
        st.divider()
