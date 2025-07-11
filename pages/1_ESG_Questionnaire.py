import streamlit as st
import pandas as pd
from utils import search_articles, assess_article

# --- Fixed ESG Due Diligence Questions ---
esg_questions = [
    "Does your company have a policy for the responsible sourcing of minerals from conflict-affected and high risk areas, that is aligned with the OECD Due Diligence Guidance for Responsible Supply Chains of Minerals from Conflict-Affected and High-Risk Areas?",
    "Has your company established an internal management structure to support supply chain due diligence and manage ESG risks?",
    "Has your company established a process to obtain chain of custody information (identification and validation of suppliers and raw materials?)",
    "Has your company established a grievance mechanism / reporting channel available to employees and contractors, as well as external stakeholders (such as local community members) to raise concerns (in a confidential manner) without fear of reprisal?",
    "Has your company established a process to collect, identify and assess risks in the supply chain, including serious human rights abuses, support to non-state armed groups or public or private security forces, financial crime linked to extraction, processing and trade of minerals, non-payment of taxes, fees and royalties to the government?",
    "Has your company established a process to mitigate risks identified in the mineral supply chain?",
    "Does your company verify the sourcing practices of smelters and/or refiners in your supply chain using third-party assurance programmes such as RMI RMAP and other?",
    "Does your company report on the supply chain due diligence measures as part of the annual disclosures?",
    "Does your company have a management person or persons responsible for sustainability topics?",
    "Does your company publish an ESG/Sustainability Report?",
    "Is the most recent ESG/Sustainability Report published according to a globally accepted standards?",
    "Has your company established a Business Ethics Policy/ Anti-Bribery Policy or similar?",
    "Does your company provide regular training and resources to employees on legal and ethical business conduct, including anti-corruption policies?",
    "Does your company have a policy to ensure that enslaved or involuntary labour of any kind, including prison labour or debt bondage and human trafficking are not used?"
]

st.set_page_config(page_title="ESG Questionnaire", layout="wide")
st.title("📋 ESG Questionnaire Autocomplete")

supplier = st.text_input("Enter supplier name:", placeholder="e.g. Huayou")
material = st.text_input("Enter material (e.g., cobalt, lithium):")

if st.button("Answer All Questions"):
    if not supplier or not material:
        st.error("Please enter a supplier and material.")
    else:
        st.info("🔍 Searching and analyzing... this may take a minute.")

        answers = []
        for i, question in enumerate(esg_questions, start=1):
            search_query = f"{supplier} {material} {question.split('?')[0]}"
            results = search_articles(search_query)

            best_score = 0
            best_result = None

            for result in results:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                url = result.get("link", "")
                assessment = assess_article(title, snippet, url, {
                    "labor": 33, "environment": 33, "governance": 34
                })
                if assessment["Weighted Risk Score"] > best_score:
                    best_score = assessment["Weighted Risk Score"]
                    best_result = {
                        "Title": title,
                        "URL": url,
                        "Risk": best_score
                    }

            if best_result:
                answer = "Yes" if best_score < 5 else "No" if best_score > 7 else "Unclear"
                answers.append({
                    "#": i,
                    "Question": question,
                    "Auto Answer": answer,
                    "Risk Score": round(best_result["Risk"], 2),
                    "Evidence Title": best_result["Title"],
                    "Evidence Link": best_result["URL"]
                })
            else:
                answers.append({
                    "#": i,
                    "Question": question,
                    "Auto Answer": "No Evidence Found",
                    "Risk Score": "-",
                    "Evidence Title": "-",
                    "Evidence Link": "-"
                })

        df = pd.DataFrame(answers)
        st.success("✅ Questionnaire completed.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"{supplier}_ESG_Questionnaire.csv",
            mime="text/csv"
        )
