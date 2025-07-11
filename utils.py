from utils import search_articles, assess_article
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
    # ... (same as before; copy your full dictionary here)
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
