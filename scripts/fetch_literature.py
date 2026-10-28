#!/usr/bin/env python3
"""
fetch_literature.py — Varredura diária no PubMed (7 blocos + vetores incondicional) e bioRxiv
Gera: data/literature_capture_raw.json
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import datetime
import time
import os
import ssl

ssl_ctx = ssl._create_unverified_context()
TODAY = datetime.date.today().isoformat()
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_RAW = os.path.join(REPO_DIR, "data", "literature_capture_raw.json")

print(f"Executing literature search for {TODAY}...")

queries = {
    "vetores_amplo": "(Aedes OR Anopheles OR Culex OR Culicidae OR mosquito OR Nyssorhynchus)",
    "arboviroses": "(dengue OR Zika OR chikungunya OR Oropouche) AND (vector OR mosquito OR antiviral OR replication)",
    "malaria_vetor": "(Plasmodium OR malaria) AND (sporozoite OR salivary gland OR cerebral malaria OR Anopheles OR mosquito OR transmission)",
    "imunometabolismo": "(trained immunity OR immunometabolism OR high-fat diet) AND (infection OR innate immunity)",
    "polifosfato_ultraestrutura": "(polyphosphate OR acidocalcisome) OR (volume electron microscopy OR FIB-SEM OR serial block face)",
    "neuro_eixo": "(insect OR mosquito OR Drosophila) AND (neuropeptide OR gut-brain OR nervous system OR brain)",
    "pragas_lepidopteros": "(Anticarsia OR Spodoptera OR Lepidoptera OR Helicoverpa) AND (hemocyte OR Bacillus thuringiensis OR gut immunity OR midgut OR RNAi)"
}

base_esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
base_efetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

found_pmids = {}
amplo_vetores_count = 0

for qname, qterm in queries.items():
    params = {
        "db": "pubmed",
        "term": qterm,
        "reldate": "2", # últimas 48h
        "datetype": "edat",
        "retmode": "json",
        "retmax": "40",
        "sort": "pub_date"
    }
    url = f"{base_esearch}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LUCHM-Literature-Bot/1.0 (fabiomg@biof.ufrj.br)'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            id_list = data.get("esearchresult", {}).get("idlist", [])
            print(f"Query {qname}: {len(id_list)} hits")
            if qname == "vetores_amplo":
                amplo_vetores_count = len(id_list)
            for pmid in id_list:
                if pmid not in found_pmids:
                    found_pmids[pmid] = []
                found_pmids[pmid].append(qname)
    except Exception as e:
        print(f"Error querying {qname}: {e}")
    time.sleep(0.35)

print(f"Total unique PMIDs: {len(found_pmids)}")

# Fetch metadata in batches of 50
articles = []
pmid_list = list(found_pmids.keys())

for i in range(0, len(pmid_list), 50):
    batch = pmid_list[i:i+50]
    params = {
        "db": "pubmed",
        "id": ",".join(batch),
        "retmode": "xml"
    }
    url = f"{base_efetch}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LUCHM-Literature-Bot/1.0 (fabiomg@biof.ufrj.br)'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            
            for article in root.findall(".//PubmedArticle"):
                pmid_el = article.find(".//MedlineCitation/PMID")
                pmid = pmid_el.text if pmid_el is not None else ""
                
                title_el = article.find(".//ArticleTitle")
                title = "".join(title_el.itertext()) if title_el is not None else "Sem título"
                
                journal_el = article.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else ""
                if not journal:
                    journal_iso = article.find(".//Journal/ISOAbbreviation")
                    journal = journal_iso.text if journal_iso is not None else "Revista não informada"
                    
                year_el = article.find(".//JournalIssue/PubDate/Year")
                if year_el is not None:
                    year = year_el.text
                else:
                    medline_date = article.find(".//JournalIssue/PubDate/MedlineDate")
                    year = medline_date.text[:4] if medline_date is not None else str(datetime.date.today().year)
                    
                abstract_texts = article.findall(".//Abstract/AbstractText")
                abstract = "\n".join("".join(t.itertext()) for t in abstract_texts if "".join(t.itertext()))
                
                authors = []
                for author in article.findall(".//AuthorList/Author"):
                    last = author.find("LastName")
                    init = author.find("Initials")
                    if last is not None:
                        name = last.text + (f" {init.text}" if init is not None else "")
                        authors.append(name)
                authors_str = ", ".join(authors) if authors else "Autores não informados"
                
                doi = ""
                for id_el in article.findall(".//ArticleIdList/ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = id_el.text
                        break
                        
                articles.append({
                    "pmid": pmid,
                    "doi": doi,
                    "titulo": title.strip(),
                    "revista": journal.strip(),
                    "ano": year,
                    "autores": authors_str,
                    "resumo_original": abstract.strip(),
                    "consultas": found_pmids.get(pmid, []),
                    "data_fonte": TODAY,
                    "fonte_captura": "PubMed"
                })
    except Exception as e:
        print(f"Error fetching batch {i}: {e}")
    time.sleep(0.4)

# BioRxiv preprints
biorxiv_queries = ["malaria", "plasmodium", "aedes", "anopheles"]
for bq in biorxiv_queries:
    try:
        bx_url = f"https://api.biorxiv.org/details/biorxiv/{TODAY}/{TODAY}/0/json"
        req = urllib.request.Request(bx_url, headers={'User-Agent': 'LUCHM-Literature-Bot/1.0 (fabiomg@biof.ufrj.br)'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            bdata = json.loads(resp.read().decode())
            for item in bdata.get("collection", []):
                tit = item.get("biorxiv_title", "")
                abst = item.get("biorxiv_abstract", "")
                if bq in tit.lower() or bq in abst.lower():
                    articles.append({
                        "pmid": item.get("biorxiv_doi", ""),
                        "doi": item.get("biorxiv_doi", ""),
                        "titulo": tit.strip(),
                        "revista": "bioRxiv",
                        "ano": TODAY[:4],
                        "autores": item.get("biorxiv_author", "Autores bioRxiv"),
                        "resumo_original": abst.strip(),
                        "consultas": [f"biorxiv_{bq}"],
                        "data_fonte": TODAY,
                        "fonte_captura": "preprint"
                    })
    except Exception as e:
        print(f"BioRxiv query error ({bq}): {e}")

# Save capture
os.makedirs(os.path.dirname(OUT_RAW), exist_ok=True)
with open(OUT_RAW, "w", encoding="utf-8") as f:
    json.dump({
        "data": TODAY,
        "amplo_vetores_count": amplo_vetores_count,
        "total": len(articles),
        "articles": articles
    }, f, ensure_ascii=False, indent=2)

print(f"Saved {len(articles)} raw articles to {OUT_RAW}")
