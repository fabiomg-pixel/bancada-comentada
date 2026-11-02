#!/usr/bin/env python3
"""
fetch_literature_v6.py — Varredura calibrada com o protocolo LUCHM v6
Captura artigos recentes (PubMed + bioRxiv) diretamente ancorados nos programas de pesquisa.
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import time
import os
import ssl
import re

ssl_ctx = ssl._create_unverified_context()
fuso_br = timezone(timedelta(hours=-3))
TODAY = datetime.now(fuso_br).strftime("%Y-%m-%d")

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_RAW = os.path.join(REPO_DIR, "data", "literature_capture_raw.json")

print(f"🚀 [v6] Executando varredura calibrada para {TODAY} (Horário de Brasília)...")

# Consultas específicas de alta fidelidade LUCHM
queries = {
    "malaria_vetor": "(Plasmodium OR malaria) AND (sporozoite OR \"salivary gland\" OR \"cerebral malaria\" OR Anopheles OR transmission OR PbA OR Pfs25 OR gametocyte)",
    "vetores_mecanismo": "(Aedes OR Anopheles OR Culex OR mosquito) AND (immunity OR midgut OR microbiota OR \"vector competence\" OR \"salivary gland\" OR \"blood meal\" OR hemocyte OR saliva OR neuropeptide OR RNAi OR Toll OR Imd OR antimicrobial)",
    "imunometabolismo": "(\"trained immunity\" OR immunometabolism OR \"high-fat diet\" OR \"metabolic reprogramming\") AND (infection OR \"innate immunity\" OR macrophage OR inflammation OR mosquito)",
    "polifosfato_ultraestrutura": "(polyphosphate OR acidocalcisome OR \"inorganic polyphosphate\" OR VTC4) OR (\"volume electron microscopy\" OR \"FIB-SEM\" OR \"serial block face\" OR \"Cryo-ET\" OR \"cryo-electron\")",
    "neuro_eixo": "(insect OR mosquito OR Drosophila) AND (neuropeptide OR \"gut-brain\" OR \"nervous system\" OR tachykinin OR leucokinin OR \"circadian rhythm\" OR sensory)",
    "lepidopteros_bt": "(Anticarsia OR Spodoptera OR Lepidoptera OR Helicoverpa) AND (hemocyte OR \"Bacillus thuringiensis\" OR Cry1Ac OR \"gut immunity\" OR RNAi OR midgut)"
}

# Filtro estrito de ruído (v6) — corta imediatamente epidemiologia de campo clínica/veterinária sem bancada
STRICT_EXCLUDE_TERMS = [
    r"\btoothpaste\b", r"\benamel\b", r"\bdental\b", r"\baerogel\b", r"\blithium\b",
    r"\bflame-retardant\b", r"\bflame retardant\b", r"\bldpe\b", r"\bsoil phosphorus\b",
    r"\brift valley fever\b.*?\b(livestock|cattle|wildlife|uganda)\b",
    r"\bcrimean-congo\b.*?\b(livestock|ticks)\b",
    r"\bbrucellosis\b", r"\bferal pigs\b", r"\bsturgeon\b", r"\bosteoarthritis\b",
    r"\bpediatric emergency\b", r"\bchild neurology\b", r"\bheart transplantation\b",
    r"\bknowledge, attitudes\b", r"\bquestionnaire survey\b", r"\bself-reported\b",
    r"\blymphatic filariasis\b.*?\bindonesia\b", r"\bpotosi virus\b", r"\bzoster vaccine\b"
]

base_esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
base_efetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

found_pmids = {}

for qname, qterm in queries.items():
    # Janela de 4 dias para garantir cobertura pós fim de semana
    params = {
        "db": "pubmed",
        "term": qterm,
        "reldate": "4",
        "datetype": "edat",
        "retmode": "json",
        "retmax": "35",
        "sort": "pub_date"
    }
    url = f"{base_esearch}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LUCHM-Literature-Bot/1.0 (fabiomg@biof.ufrj.br)'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            id_list = data.get("esearchresult", {}).get("idlist", [])
            print(f"  • {qname}: {len(id_list)} hits")
            for pmid in id_list:
                if pmid not in found_pmids:
                    found_pmids[pmid] = []
                found_pmids[pmid].append(qname)
    except Exception as e:
        print(f"Erro na query {qname}: {e}")
    time.sleep(0.35)

print(f"Total de PMIDs únicos encontrados: {len(found_pmids)}")

# Fetch metadata dos PMIDs
articles = []
pmid_list = list(found_pmids.keys())

for i in range(0, len(pmid_list), 40):
    batch = pmid_list[i:i+40]
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
                    year = medline_date.text[:4] if medline_date is not None else TODAY[:4]
                    
                abstract_texts = article.findall(".//Abstract/AbstractText")
                abstract = "\n".join("".join(t.itertext()) for t in abstract_texts if "".join(t.itertext()))
                
                # Checagem de ruído estrito
                full_text_to_check = f"{title} {abstract}".lower()
                if any(re.search(pat, full_text_to_check, re.I) for pat in STRICT_EXCLUDE_TERMS):
                    continue

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
        print(f"Erro buscando metadados (batch {i}): {e}")
    time.sleep(0.4)

# BioRxiv Preprints recentes
biorxiv_terms = ["plasmodium", "malaria", "aedes", "anopheles", "polyphosphate", "acidocalcisome"]
for bq in biorxiv_terms:
    try:
        # Busca últimos 3 dias
        d_start = (datetime.now(fuso_br) - timedelta(days=3)).strftime("%Y-%m-%d")
        bx_url = f"https://api.biorxiv.org/details/biorxiv/{d_start}/{TODAY}/0/json"
        req = urllib.request.Request(bx_url, headers={'User-Agent': 'LUCHM-Literature-Bot/1.0 (fabiomg@biof.ufrj.br)'})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            bdata = json.loads(resp.read().decode())
            for item in bdata.get("collection", []):
                tit = item.get("biorxiv_title", "")
                abst = item.get("biorxiv_abstract", "")
                full_bx = f"{tit} {abst}".lower()
                if bq in full_bx:
                    if any(re.search(pat, full_bx, re.I) for pat in STRICT_EXCLUDE_TERMS):
                        continue
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
        pass

# Deduplicação por DOI e PMID
dedup = {}
for a in articles:
    key = a.get("doi") or a.get("pmid")
    if key and key not in dedup:
        dedup[key] = a

final_list = list(dedup.values())
print(f"✅ Varredura v6 concluída: {len(final_list)} artigos após deduplicação e filtro estrito de ruído.")

os.makedirs(os.path.dirname(OUT_RAW), exist_ok=True)
with open(OUT_RAW, "w", encoding="utf-8") as f:
    json.dump({
        "data": TODAY,
        "total": len(final_list),
        "articles": final_list
    }, f, ensure_ascii=False, indent=2)

print(f"Salvo em: {OUT_RAW}")
