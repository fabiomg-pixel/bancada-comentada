#!/usr/bin/env python3
"""
importar_v6.py — entrada da literatura no espelho do GitHub (desde 09/11/2026)

A Bancada Comentada oficial é a revista do claude.ai, alimentada pela rotina
"Resumo da Literatura Científica v6". Este repositório é o espelho dela e não
faz captura própria: a tarefa agendada "Espelho da Bancada no GitHub" grava,
em dias úteis, o depósito do dia em data/captura_v6/AAAA-MM-DD.json.

Este script lê o arquivo mais recente de data/captura_v6/, busca o resumo
original de cada artigo pelo identificador (PubMed por PMID, bioRxiv por DOI;
isto é leitura de metadados dos mesmos artigos, não busca nova) e grava
data/literature_capture_raw.json no formato que reclassificar.py já lê.

Códigos de saída: 0 = importou; 10 = nada novo (o arquivo mais recente já foi
importado, ou não existe arquivo); 1 = erro de leitura do arquivo de captura.
"""

import glob
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURA_DIR = os.path.join(REPO_DIR, "data", "captura_v6")
OUT_RAW = os.path.join(REPO_DIR, "data", "literature_capture_raw.json")
UA = {"User-Agent": "LUCHM-Bancada-Espelho/1.0"}
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NADA_NOVO = 10


def arquivo_mais_recente():
    arquivos = sorted(
        f for f in glob.glob(os.path.join(CAPTURA_DIR, "*.json"))
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", os.path.basename(f))
    )
    return arquivos[-1] if arquivos else None


def ja_importado(nome):
    if not os.path.exists(OUT_RAW):
        return False
    try:
        with open(OUT_RAW, encoding="utf-8") as f:
            return json.load(f).get("arquivo_captura") == nome
    except (OSError, ValueError):
        return False


def resumos_pubmed(pmids):
    """PMID -> resumo original. Falha de rede devolve o que conseguiu."""
    saida = {}
    for i in range(0, len(pmids), 40):
        lote = pmids[i:i + 40]
        url = f"{EFETCH}?{urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(lote), 'retmode': 'xml'})}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as resp:
                raiz = ET.fromstring(resp.read())
            for art in raiz.findall(".//PubmedArticle"):
                pmid_el = art.find(".//MedlineCitation/PMID")
                if pmid_el is None:
                    continue
                partes = ["".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText")]
                texto = "\n".join(p for p in partes if p).strip()
                if texto:
                    saida[pmid_el.text] = texto
        except Exception as erro:  # rede ou XML: segue com o resumo da v6
            print(f"   ⚠️ PubMed (lote {i}): {erro}")
        time.sleep(0.4)
    return saida


def resumo_biorxiv(doi):
    try:
        url = f"https://api.biorxiv.org/details/biorxiv/{urllib.parse.quote(doi, safe='/')}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as resp:
            colecao = json.loads(resp.read().decode()).get("collection", [])
        return (colecao[-1].get("abstract") or "").strip() if colecao else ""
    except Exception:
        return ""


def main():
    caminho = arquivo_mais_recente()
    if not caminho:
        print("Nenhum arquivo em data/captura_v6/: nada a importar.")
        return NADA_NOVO
    nome = os.path.basename(caminho)
    if ja_importado(nome):
        print(f"{nome} já foi importado: nada novo.")
        return NADA_NOVO
    try:
        with open(caminho, encoding="utf-8") as f:
            captura = json.load(f)
    except (OSError, ValueError) as erro:
        print(f"❌ Não consegui ler {nome}: {erro}")
        return 1

    itens = captura.get("artigos", [])
    pmids = [str(a["pmid"]) for a in itens if str(a.get("pmid") or "").isdigit()]
    resumos = resumos_pubmed(pmids)

    artigos = []
    for a in itens:
        pmid = str(a.get("pmid") or "").strip()
        doi = (a.get("doi") or "").strip()
        preprint = a.get("tipo") == "preprint" or a.get("fonte_captura") == "preprint"
        original = resumos.get(pmid, "") if pmid.isdigit() else ""
        if not original and preprint and doi:
            original = resumo_biorxiv(doi)
        artigos.append({
            "pmid": pmid or doi,
            "doi": doi,
            "titulo": (a.get("titulo") or "").strip(),
            "revista": a.get("revista") or ("bioRxiv" if preprint else ""),
            "ano": str(a.get("ano") or (a.get("data_fonte") or "")[:4]),
            "autores": a.get("autores") or "Autores não informados",
            "resumo_original": original or (a.get("resumo") or ""),
            "consultas": [a["consulta"]] if a.get("consulta") else [],
            "data_fonte": a.get("data_fonte") or captura.get("data"),
            "fonte_captura": "preprint" if preprint else "PubMed",
            "v6": {k: a.get(k) for k in ("tema", "importancia", "prioridade", "score", "implicacao", "resumo", "metodo") if a.get(k) not in (None, "")},
        })

    os.makedirs(os.path.dirname(OUT_RAW), exist_ok=True)
    with open(OUT_RAW, "w", encoding="utf-8") as f:
        json.dump({
            "data": captura.get("data"),
            "total": len(artigos),
            "origem": "espelho da revista do claude.ai (Resumo da Literatura Científica v6)",
            "arquivo_captura": nome,
            "articles": artigos,
        }, f, ensure_ascii=False, indent=2)
    com_original = sum(1 for a, i in zip(artigos, itens) if a["resumo_original"] and a["resumo_original"] != (i.get("resumo") or ""))
    print(f"✅ {nome}: {len(artigos)} artigos importados ({com_original} com resumo original).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
