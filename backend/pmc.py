import requests
import random
import logging

def mine_pmc_text() -> dict:
    """
    Mine a random relevant taxonomic text from PubMed Central.
    Returns a dict with 'title', 'text', and 'source'.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pmc",
        "term": "arthropod taxonomy new species",
        "retmode": "json",
        "retmax": 100
    }

    try:
        res = requests.get(search_url, params=search_params, timeout=10)
        res.raise_for_status()
        data = res.json()
        idlist = data.get("esearchresult", {}).get("idlist", [])

        if not idlist:
            raise ValueError("No relevant PMC articles found.")

        # Try fetching up to 5 random articles until we find a suitable passage
        random.shuffle(idlist)
        for pmcid in idlist[:5]:
            try:
                # Add 'PMC' prefix to the ID
                fetch_url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{pmcid}/unicode"
                f_res = requests.get(fetch_url, timeout=10)
                f_res.raise_for_status()
                f_data = f_res.json()

                # Bioc JSON format structure:
                # [ { "documents": [ { "passages": [ { "text": "...", "infons": { ... } } ] } ] } ]
                if not f_data or not isinstance(f_data, list):
                    continue

                documents = f_data[0].get("documents", [])
                if not documents:
                    continue

                passages = documents[0].get("passages", [])

                title = "Unknown Title"
                # Find title passage (often the first one, or infons.type == "title")
                for p in passages:
                    infons = p.get("infons", {})
                    if infons.get("type", "").lower() == "title" or infons.get("section_type", "").lower() == "title":
                        title = p.get("text", title)
                        break
                if title == "Unknown Title" and passages:
                    # Fallback to the first passage text
                    title_candidate = passages[0].get("text", "")
                    if len(title_candidate) < 200:
                        title = title_candidate

                # Find a relevant text passage
                # Criteria: > 200 chars, < 5000 chars, contains "length", "mm", "sp. nov." or other taxonomic keywords
                best_passage = None
                for p in passages:
                    text = p.get("text", "").strip()
                    if 200 < len(text) < 5000:
                        text_lower = text.lower()
                        if any(kw in text_lower for kw in ["mm", "length", "color", "species"]):
                            best_passage = text
                            break

                if best_passage:
                    return {
                        "title": title,
                        "text": best_passage,
                        "source": f"PMC{pmcid}"
                    }
            except Exception as e:
                logging.warning(f"Failed to fetch PMC{pmcid}: {e}")
                continue

        raise ValueError("Failed to find a suitable text passage in the sampled PMC articles.")

    except Exception as e:
        logging.error(f"Error mining PMC text: {e}")
        raise
