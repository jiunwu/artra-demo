import requests
import random
import logging

def search_pmc(term: str, limit: int = 10) -> list:
    """
    Search PubMed Central for articles matching the given term and fetch their texts.
    Returns a list of dicts with 'title', 'text', and 'source'.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pmc",
        "term": term,
        "retmode": "json",
        "retmax": min(limit * 2, 100) # Fetch more IDs to account for empty/unparseable ones
    }

    results = []

    try:
        res = requests.get(search_url, params=search_params, timeout=10)
        res.raise_for_status()
        data = res.json()
        idlist = data.get("esearchresult", {}).get("idlist", [])

        if not idlist:
            return results

        for pmcid in idlist:
            if len(results) >= limit:
                break

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
                # Find title passage
                for p in passages:
                    infons = p.get("infons", {})
                    if infons.get("type", "").lower() == "title" or infons.get("section_type", "").lower() == "title":
                        title = p.get("text", title)
                        break

                if title == "Unknown Title" and passages:
                    title_candidate = passages[0].get("text", "")
                    if len(title_candidate) < 200:
                        title = title_candidate

                # Just take the abstract, or the first substantial passage if no abstract
                best_passage = None

                # Try abstract first
                for p in passages:
                    infons = p.get("infons", {})
                    if "abstract" in infons.get("section_type", "").lower():
                        best_passage = p.get("text", "").strip()
                        break

                # If no abstract, take a reasonably sized passage
                if not best_passage:
                    for p in passages:
                        text = p.get("text", "").strip()
                        if 300 < len(text) < 5000:
                            best_passage = text
                            break

                # Fallback to combining a few passages
                if not best_passage:
                    combined = []
                    chars = 0
                    for p in passages[1:5]: # skip title
                        text = p.get("text", "").strip()
                        if text:
                            combined.append(text)
                            chars += len(text)
                            if chars > 500:
                                break
                    best_passage = " ".join(combined)

                if best_passage and len(best_passage) > 50:
                    results.append({
                        "title": title,
                        "text": best_passage,
                        "source": f"PMC{pmcid}"
                    })
            except Exception as e:
                logging.warning(f"Failed to fetch PMC{pmcid}: {e}")
                continue

        return results

    except Exception as e:
        logging.error(f"Error searching PMC: {e}")
        raise


def mine_pmc_text() -> dict:
    """
    Mine a random relevant taxonomic text from PubMed Central.
    Returns a dict with 'title', 'text', and 'source'.
    """
    results = search_pmc("arthropod taxonomy new species", limit=5)
    if not results:
        raise ValueError("Failed to find a suitable text passage in the sampled PMC articles.")
    return random.choice(results)
