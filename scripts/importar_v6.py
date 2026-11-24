#!/usr/bin/env python3
"""
importar_v6.py — Entrada da literatura no espelho do GitHub (desde 09/11/2026)

A Bancada Comentada oficial é a revista do claude.ai, alimentada pela rotina
"Resumo da Literatura Científica v6". Este repositório é o espelho dela e não
faz captura própria: a tarefa agendada "Espelho da Bancada no GitHub" grava,
em dias úteis, o depósito do dia em data/captura_v6/AAAA-MM-DD.json.

Otimizações v2:
- Consolida a janela rolante de 14 dias (DIAS_CIRCULACAO = 14) a partir dos
  arquivos em data/captura_v6/, ativando o seletor diário do Radar e das abas.
- Reaproveita resumos originais já baixados em execuções anteriores (buscando no
  PubMed/bioRxiv apenas identificadores inéditos).
- Preserva metadados diários para alimentar a coleção `radar` da interface web.

Códigos de saída: 0 = importou; 10 = nada novo (o arquivo mais recente já foi
importado com janela de 14 dias ativa, exceto com --forcar); 1 = erro de leitura.
"""

import argparse
import concurrent.futures
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURA_DIR = os.path.join(REPO_DIR, "data", "captura_v6")
OUT_RAW = os.path.join(REPO_DIR, "data", "literature_capture_raw.json")
EDICAO_ATUAL = os.path.join(REPO_DIR, "data", "edicao_atual.json")
UA = {"User-Agent": "LUCHM-Bancada-Espelho/2.0"}
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NADA_NOVO = 10
DIAS_JANELA = 14


def listar_arquivos_captura():
    return sorted(
        f for f in glob.glob(os.path.join(CAPTURA_DIR, "*.json"))
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", os.path.basename(f))
    )


def eh_abstract_ingles_real(txt: str) -> bool:
    if not txt or len(txt) < 180:
        return False
    t = " " + txt.lower() + " "
    en = sum(1 for w in [" the ", " and ", " with ", " that ", " were ", " from ", " this "] if w in t)
    pt = sum(1 for w in [" de ", " do ", " da ", " para ", " com ", " que ", " após "] if w in t)
    return en >= 3 and en > pt


def carregar_resumos_conhecidos():
    """Carrega abstracts em inglês já obtidos anteriormente para evitar chamadas repetidas."""
    conhecidos = {}
    for caminho in (OUT_RAW, EDICAO_ATUAL):
        if not os.path.exists(caminho):
            continue
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
            if "articles" in dados and isinstance(dados["articles"], list):
                for a in dados["articles"]:
                    ident = str(a.get("pmid") or a.get("doi") or "").strip()
                    res_orig = (a.get("resumo_original") or "").strip()
                    if ident and eh_abstract_ingles_real(res_orig):
                        conhecidos[ident] = res_orig
            if "colecao_artigos" in dados and isinstance(dados["colecao_artigos"], dict):
                for k, a in dados["colecao_artigos"].items():
                    ident = str(a.get("pmid") or a.get("doi") or k).strip()
                    res_orig = (a.get("resumo_original") or a.get("resumo") or "").strip()
                    if ident and eh_abstract_ingles_real(res_orig):
                        conhecidos.setdefault(ident, res_orig)
        except Exception:
            pass
    return conhecidos


def http_get_bytes(url: str, timeout: int = 25) -> bytes:
    """Usa curl nativo (que respeita o Keychain TLS do macOS) com fallback para urllib."""
    if shutil.which("curl"):
        res = subprocess.run(
            ["curl", "-fsSL", "--max-time", str(timeout), "-A", UA["User-Agent"], url],
            capture_output=True,
        )
        if res.returncode == 0 and res.stdout:
            return res.stdout
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as resp:
        return resp.read()


def resumos_pubmed(pmids):
    """PMID -> resumo original em lotes de 120."""
    saida = {}
    if not pmids:
        return saida
    for i in range(0, len(pmids), 120):
        lote = pmids[i:i + 120]
        url = f"{EFETCH}?{urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(lote), 'retmode': 'xml'})}"
        try:
            raw_xml = http_get_bytes(url, timeout=30)
            raiz = ET.fromstring(raw_xml)
            for art in raiz.findall(".//PubmedArticle"):
                pmid_el = art.find(".//MedlineCitation/PMID")
                if pmid_el is None:
                    continue
                partes = ["".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText")]
                texto = "\n".join(p for p in partes if p).strip()
                pmc_id = ""
                for aid_el in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
                    if aid_el.attrib.get("IdType") == "pmc" and aid_el.text:
                        pmc_id = aid_el.text.strip()
                        break
                if texto or pmc_id:
                    saida[pmid_el.text] = {"abstract": texto, "pmc": pmc_id}
        except Exception as erro:
            print(f"   ⚠️ PubMed (lote {i}): {erro}")
        if i + 120 < len(pmids):
            time.sleep(0.35)
    return saida


def resumo_preprint(doi):
    for servidor in ("biorxiv", "medrxiv"):
        try:
            url = f"https://api.biorxiv.org/details/{servidor}/{urllib.parse.quote(doi, safe='/')}"
            raw = http_get_bytes(url, timeout=12)
            colecao = json.loads(raw.decode()).get("collection", [])
            if colecao:
                txt = (colecao[-1].get("abstract") or "").strip()
                if txt:
                    return txt
        except Exception:
            continue
    return ""


def ja_importado(nome_mais_recente, qtd_arquivos_janela):
    if not os.path.exists(OUT_RAW):
        return False
    try:
        with open(OUT_RAW, encoding="utf-8") as f:
            atual = json.load(f)
        return (
            atual.get("arquivo_captura") == nome_mais_recente
            and len(atual.get("edicoes_janela") or []) == qtd_arquivos_janela
        )
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description="Importa capturas v6 em janela rolante de 14 dias.")
    parser.add_argument("--forcar", action="store_true", help="Reimporta mesmo se o arquivo mais recente já constar.")
    args, _ = parser.parse_known_args()

    arquivos = listar_arquivos_captura()
    if not arquivos:
        print("Nenhum arquivo em data/captura_v6/: nada a importar.")
        return NADA_NOVO

    caminho_recente = arquivos[-1]
    nome_recente = os.path.basename(caminho_recente)
    data_ref_str = nome_recente.replace(".json", "")
    data_ref = dt.date.fromisoformat(data_ref_str)
    data_corte = data_ref - dt.timedelta(days=DIAS_JANELA)

    arquivos_janela = [
        f for f in arquivos
        if dt.date.fromisoformat(os.path.basename(f).replace(".json", "")) >= data_corte
    ]

    if not args.forcar and ja_importado(nome_recente, len(arquivos_janela)):
        print(f"{nome_recente} (janela de {len(arquivos_janela)} edições) já foi importado: nada novo.")
        return NADA_NOVO

    capturas_lidas = []
    for arq in arquivos_janela:
        try:
            with open(arq, encoding="utf-8") as f:
                cap = json.load(f)
            capturas_lidas.append((os.path.basename(arq), cap))
        except (OSError, ValueError) as erro:
            if arq == caminho_recente:
                print(f"❌ Não consegui ler {nome_recente}: {erro}")
                return 1
            print(f"   ⚠️ Ignorando captura antiga ilegível {os.path.basename(arq)}: {erro}")

    conhecidos = carregar_resumos_conhecidos()

    # Consolidar artigos únicos na janela de 14 dias (preservando data de entrada e última visualização)
    consolidados = {}
    edicoes_janela = []

    for nome_arq, cap in capturas_lidas:
        data_cap = str(cap.get("data") or nome_arq.replace(".json", ""))
        itens = cap.get("artigos", [])
        edicoes_janela.append({
            "_id": data_cap,
            "data": data_cap,
            "total": len(itens),
            "origem": cap.get("origem") or "Resumo da Literatura Científica v6",
        })
        for a in itens:
            pmid = str(a.get("pmid") or "").strip()
            doi = (a.get("doi") or "").strip()
            ident = pmid or doi
            if not ident:
                continue
            preprint = a.get("tipo") == "preprint" or "preprint" in str(a.get("fonte_captura") or "").lower() or "biorxiv" in str(a.get("revista") or "").lower()
            v6_meta = {
                k: a.get(k)
                for k in ("tema", "importancia", "prioridade", "score", "implicacao", "resumo", "metodo")
                if a.get(k) not in (None, "")
            }
            consultas_atuais = [c.strip() for c in str(a.get("consulta") or "").split(",") if c.strip()]

            if ident in consolidados:
                ex = consolidados[ident]
                ex["visto_em"] = data_cap
                for c in consultas_atuais:
                    if c not in ex["consultas"]:
                        ex["consultas"].append(c)
                if v6_meta.get("score", 0) and (v6_meta.get("score") or 0) >= (ex["v6"].get("score") or 0):
                    ex["v6"].update(v6_meta)
            else:
                consolidados[ident] = {
                    "pmid": pmid or doi,
                    "doi": doi,
                    "pmc": str(a.get("pmc") or "").strip(),
                    "titulo": (a.get("titulo") or "").strip(),
                    "revista": (a.get("revista") or ("bioRxiv" if preprint else "")).strip(),
                    "ano": str(a.get("ano") or (a.get("data_fonte") or data_cap)[:4]),
                    "autores": a.get("autores") or "Autores não informados",
                    "resumo_v6": (a.get("resumo") or "").strip(),
                    "consultas": consultas_atuais,
                    "data_fonte": a.get("data_fonte") or data_cap,
                    "entrou_em": a.get("entrou_em") or data_cap,
                    "visto_em": data_cap,
                    "fonte_captura": "preprint" if preprint else "PubMed",
                    "v6": v6_meta,
                }

    # Identificar apenas PMIDs e DOIs de preprints que ainda não têm resumo original em cache
    pmids_faltantes = [
        it["pmid"] for ident, it in consolidados.items()
        if it["pmid"].isdigit() and ident not in conhecidos
    ]
    dois_preprint_faltantes = [
        (ident, it["doi"]) for ident, it in consolidados.items()
        if not it["pmid"].isdigit() and it["fonte_captura"] == "preprint" and it["doi"] and ident not in conhecidos
    ]

    print(f"📥 Janela de 14 dias ({len(edicoes_janela)} edições até {data_ref_str}): {len(consolidados)} artigos únicos.")
    print(f"   • Resumos já em cache local: {len(consolidados) - len(pmids_faltantes) - len(dois_preprint_faltantes)} | Novos no PubMed: {len(pmids_faltantes)} | Novos preprints: {len(dois_preprint_faltantes)}")

    novos_pubmed = resumos_pubmed(pmids_faltantes)
    novos_preprints = {}
    if dois_preprint_faltantes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futs = {pool.submit(resumo_preprint, doi): ident for ident, doi in dois_preprint_faltantes}
            for fut in concurrent.futures.as_completed(futs):
                ident = futs[fut]
                try:
                    txt = fut.result()
                    if txt:
                        novos_preprints[ident] = txt
                except Exception:
                    pass

    artigos_saida = []
    com_original = 0
    for ident, it in consolidados.items():
        pm_info = novos_pubmed.get(it["pmid"], {})
        original = (
            pm_info.get("abstract")
            or novos_preprints.get(ident)
            or conhecidos.get(ident)
            or ""
        )
        pmc_id = pm_info.get("pmc") or it.get("pmc") or ""
        if original:
            com_original += 1
        artigos_saida.append({
            "pmid": it["pmid"],
            "doi": it["doi"],
            "pmc": pmc_id,
            "titulo": it["titulo"],
            "revista": it["revista"],
            "ano": it["ano"],
            "autores": it["autores"],
            "resumo_original": original or it["resumo_v6"],
            "resumo_pt_v6": it["resumo_v6"],
            "consultas": it["consultas"],
            "data_fonte": it["data_fonte"],
            "entrou_em": it["entrou_em"],
            "visto_em": it["visto_em"],
            "fonte_captura": it["fonte_captura"],
            "v6": it["v6"],
        })

    os.makedirs(os.path.dirname(OUT_RAW), exist_ok=True)
    tmp_out = OUT_RAW + ".tmp"
    with open(tmp_out, "w", encoding="utf-8") as f:
        json.dump({
            "data": data_ref_str,
            "total": sum(1 for a in artigos_saida if a["visto_em"] == data_ref_str),
            "total_janela_14d": len(artigos_saida),
            "origem": "espelho da revista do claude.ai (Resumo da Literatura Científica v6)",
            "arquivo_captura": nome_recente,
            "edicoes_janela": edicoes_janela,
            "articles": artigos_saida,
        }, f, ensure_ascii=False, indent=2)
    os.replace(tmp_out, OUT_RAW)

    hoje_n = sum(1 for a in artigos_saida if a["visto_em"] == data_ref_str)
    print(f"✅ {nome_recente}: {hoje_n} artigos do dia | {len(artigos_saida)} na janela de 14d ({com_original} com abstract integral).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
