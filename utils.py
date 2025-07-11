import requests
from textblob import TextBlob
import nltk

# Ensure NLTK corpora
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('brown')
    nltk.download('wordnet')
    nltk.download('vader_lexicon')

# --- Risk Keywords ---
risk_keywords = {
    "labor": {
        "child labor": 3, "forced labor": 3, "bonded labor": 3, "modern slavery": 3,
        "human trafficking": 3, "unsafe working conditions": 2, "low wages": 1,
        "wage theft": 2, "long working hours": 1, "long hours": 1,
        "no union": 1, "union suppression": 2, "anti-union practices": 2,
        "worker abuse": 2, "discrimination": 1, "gender-based violence": 2,
        "sexual harassment": 2, "exploitation": 2, "labor violations": 2,
        "migrant worker abuse": 2, "hazardous working conditions": 2,
        "worker deaths": 3, "occupational hazard": 2, "factory collapse": 3,
        "temporary contracts": 1, "unpaid overtime": 2, "lack of health insurance": 1,
        "retaliation": 2
    },
    "environment": {
        "pollution": 2, "air pollution": 2, "water pollution": 2, "soil contamination": 2,
        "deforestation": 3, "biodiversity loss": 3, "habitat destruction": 3,
        "water contamination": 2, "toxic waste": 3, "oil spill": 3, "chemical spill": 2,
        "emissions violation": 2, "illegal logging": 3, "ecosystem destruction": 3,
        "environmental damage": 2, "climate impact": 2, "greenhouse gas emissions": 2,
        "carbon emissions": 2, "methane emissions": 2, "illegal dumping": 2,
        "waste mismanagement": 1, "overconsumption": 1, "excessive packaging": 1,
        "resource depletion": 2, "water overuse": 2, "tailings dam": 3,
        "dam collapse": 3, "brumadinho": 3, "toxic sludge": 3,
        "mining disaster": 3, "environmental catastrophe": 3, "negative impact": 3
    },
    "governance": {
        "sanctions": 2, "fraud": 3, "accounting fraud": 3, "corruption": 3,
        "bribery": 3, "embezzlement": 3, "money laundering": 3,
        "regulatory violation": 2, "fines": 1, "illegal practices": 2,
        "lack of transparency": 2, "governance failure": 2,
        "whistleblower retaliation": 2, "non-compliance": 2,
        "anti-competitive behavior": 2, "insider trading": 2,
        "misleading reporting": 2, "data breach": 2, "privacy violation": 2,
        "cybersecurity failure": 2, "board conflicts of interest": 2,
        "lawsuit": 2, "settlement": 2, "criminal charges": 3,
        "investigation": 2, "stock manipulation": 3
    }
}

def get_full_text(url):
    try:
        DIFFBOT_TOKEN = "070489d54ba6e1dbb01ff6c8ca766530"
        api_url = f"https://api.diffbot.com/v3/article?token={DIFFBOT_TOKEN}&url={url}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "objects" in data and len(data["objects"]) > 0:
            return data["objects"][0].get("text", "")
        return ""
    except Exception as e:
        return f"[Error extracting article text: {e}]"

def assess_article(title, snippet, url, weights):
    # Guard clause to ensure correct keys are present
    required_keys = {"labor", "environment", "governance"}
    if not required_keys.issubset(weights):
        raise ValueError(f"Missing required weight keys: {required_keys - set(weights)}")

    full_text = get_full_text(url)
    combined_text = f"{title} {snippet} {full_text}".lower()
    sentiment = TextBlob(combined_text).sentiment.polarity
    risk_scores = {k: 0 for k in risk_keywords}

    for category, terms in risk_keywords.items():
        for kw, severity in terms.items():
            if kw in combined_text:
                risk_scores[category] += severity

    weighted_score = (
        risk_scores["labor"] * weights["labor"] +
        risk_scores["environment"] * weights["environment"] +
        risk_scores["governance"] * weights["governance"]
    ) / 100

    return {
        "Labor Risk": risk_scores["labor"],
        "Environmental Risk": risk_scores["environment"],
        "Governance Risk": risk_scores["governance"],
        "Sentiment": sentiment,
        "Weighted Risk Score": round(weighted_score, 2),
        "URL": url,
        "Title": title
    }

def search_articles(query):
    GOOGLE_API_KEY = "AIzaSyCEWC7rZUu8EDPFeVtNsWrsdBv0HVcJ_dg"
    CSE_ID = "57a79da21c554499f"
    preferred_sources = [
        "site:business-humanrights.org",
        "site:ejatlas.org",
        "site:climatecasechart.com/non-us-climate-change-litigation"
    ]
    all_results = []
    url = "https://www.googleapis.com/customsearch/v1"
    for source in preferred_sources:
        full_query = f"{query} {source}"
        params = {"key": GOOGLE_API_KEY, "cx": CSE_ID, "q": full_query, "num": 5}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = [{
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet", "")
            } for item in data.get("items", [])]
            all_results.extend(results)
        except Exception as e:
            print(f"Error fetching from {source}: {e}")
    if not all_results:
        params = {"key": GOOGLE_API_KEY, "cx": CSE_ID, "q": query, "num": 10}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            all_results = [{
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet", "")
            } for item in data.get("items", [])]
        except Exception as e:
            print("Fallback search error:", e)
    return all_results
