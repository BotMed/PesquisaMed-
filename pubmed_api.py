from flask import Flask, request, jsonify
import requests
from xml.etree import ElementTree

app = Flask(__name__)

@app.route("/api/pubmed", methods=["POST"])
def search_pubmed():
    data = request.get_json()
    query = data.get("query")
    max_results = data.get("max_results", 5)

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }

    search_response = requests.get(esearch_url, params=esearch_params).json()
    id_list = search_response.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return jsonify({"results": []})

    efetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }

    fetch_response = requests.get(efetch_url, params=efetch_params)
    root = ElementTree.fromstring(fetch_response.content)

    results = []
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        journal = article.findtext(".//Journal/Title")
        year = article.findtext(".//PubDate/Year")
        pmid = article.findtext(".//PMID")

        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName")
            fore = author.findtext("ForeName")
            if last and fore:
                authors.append(f"{fore} {last}")

        results.append({
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "pmid": pmid
        })

    return jsonify({"results": results})
