#!/usr/bin/env python3
"""
enriquecer_tudo_flash38.py
Enriquece TODOS os artigos da edicao_atual.json usando Gemini 3.8 Flash.
Gera análises de bancada densas, profundas, com terminologia técnica de bancada,
métricas quantitativas, ancoragem aos programas do LUCHM e faísca lateral rica.
"""

import os
import sys
import json
import ssl
import time
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDICAO_FILE = os.path.join(REPO_DIR, "data", "edicao_atual.json")
CACHE_FILE = os.path.join(REPO_DIR, "data", "cache_flash38_artigos.json")
INDEX_HTML = os.path.join(REPO_DIR, "index.html")

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key.strip()
    env_file = os.path.expanduser("~/.faixaoculta/.env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            pass
    return ""

API_KEY = get_api_key()
MODEL_NAME = "gemini-3.8-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

SSL_CTX = ssl._create_unverified_context()

OPEN_ACCESS_PATTERNS = [
    r"malaria journal", r"frontiers", r"plos", r"nature communications",
    r"cell reports", r"medcomm", r"mbio", r"cureus", r"scientific reports",
    r"bmc", r"elife", r"communications biology", r"biorxiv", r"medrxiv",
    r"open access", r"jove", r"acta tropica", r"parasites & vectors"
]

PROGRAMAS_LUCHM = """
PROGRAMAS DE PESQUISA DO LUCHM (IBCCF/UFRJ - Prof. Fábio Gomes):
1. Malária Cerebral & Neuroinflamação (modelo murino C57BL/6J infectado com PbA; permeabilidade da barreira hematoencefálica; junções oclusivas claudina-5/occludina; astrócitos e micróglia; ferroptose endotelial e dano oxidativo).
2. Repasto Sanguíneo HFHS & Metabolismo do Vetor (fêmeas de Aedes aegypti e Anopheles; alimentação com sangue de camundongos obesos em dieta hiperlipídica/hiperglicêmica; peroxidação lipídica mediada por hemo livre; estresse oxidativo no intestino médio; gotas lipídicas e ovogênese).
3. Imunidade de Vetores & RNAi (competência vetorial para Dengue, Zika, Chikungunya e Oropouche; vias de siRNA com Dicer-2 e Argonaute-2; imunidade antiviral e priming imune transgeracional).
4. Polifosfato Inorgânico & Acidocalcisomas (homeostase de bioenergética e armazenamento de cálcio/fósforo em protozoários parasitos e insetos; enzimas exopolifosfatase e polifosfato quinase; regulação de pH vacuolar).
5. Microscopia Eletrônica de Volume & Bioimagem (CENABIO/LUCHM; reconstrução tridimensional por FIB-SEM e SBF-SEM; sítios de contato de organelas / MCS; preservação ultraestrutural e contraste de membranas com metais pesados).
6. Biologia Celular de Plasmodium & Bloqueio de Transmissão (ciclo exoeritrocítico e esporozoítos; transição intestino-glândula salivar; antígenos Pfs25 e CSP).
7. Controle de Pragas & Bioinseticidas (Anticarsia gemmatalis e Spodoptera; toxinas Cry de Bacillus thuringiensis; receptores ABCC2; mecanismos epigenéticos de resistência e integridade da membrana peritrófica).
"""

def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def analisar_com_gemini(aid, titulo, abstract, revista, ano, programa_sugerido):
    prompt = f"""Você é o avaliador científico sênior do Laboratório de Ultraestrutura Celular Hertha Meyer (LUCHM/IBCCF/UFRJ), chefiado pelo Prof. Fábio Mendonça Gomes.

Analise o artigo científico abaixo e elabore uma síntese aprofundada, técnica, densa e com terminologia rigorosa de bancada.
AVISO RIGOROSO: NUNCA gere textos curtos, genéricos ou superficiais. Cada bloco deve ser um parágrafo completo (3 a 5 frases ricas em detalhes moleculares, modelos, controles, concentrações e raciocínio biológico).

REFERÊNCIA DOS PROGRAMAS DO LABORATÓRIO:
{PROGRAMAS_LUCHM}

ARTIGO EM AVALIAÇÃO:
- ID: {aid}
- TÍTULO: {titulo}
- REVISTA: {revista} ({ano})
- ABSTRACT: {abstract}
- PROGRAMA PRÉ-ASSOCIADO: {programa_sugerido}

Gere APENAS um objeto JSON com as seguintes chaves exatas:
{{
  "programa_luchm": "Nome exato de um dos 7 programas do LUCHM mais conectado a este estudo",
  "metodo_bancada": "Parágrafo detalhado de 3 a 5 frases descrevendo o delineamento metodológico experimental real do estudo: modelos celulares/animais, preparo de amostras, cepas, dosagens/concentrações, marcações imunocitoquímicas ou fluorimétricas, controles positivos/negativos e plataformas instrumentais utilizadas.",
  "implicacao_luchm": "Parágrafo denso de 3 a 5 frases conectando explicitamente as descobertas deste trabalho com a bancada e as perguntas biológicas ativas do LUCHM no programa correspondente.",
  "faisca_lateral": "💡 Delineamento experimental concreto de 2 a 3 frases propondo um teste testável e acionável na bancada do laboratório inspirado neste trabalho.",
  "racional_bloco": "Parágrafo completo de 3 a 4 frases explicando a lacuna mecanicista na literatura, a contradição biológica abordada e a hipótese central testada pelos autores.",
  "resultados_bloco": "Parágrafo detalhado de 3 a 5 frases especificando os principais resultados experimentais, vias de sinalização demonstradas, métricas quantitativas e fenótipos comprovados."
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }

    for attempt in range(3):
        try:
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
                res_data = json.loads(resp.read().decode())
                cand = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(cand)
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
            if attempt == 2:
                print(f"[{aid}] Erro final Gemini 3.8 Flash: {e}")
                return None

def processar_artigo(aid, a, cache):
    tit = a.get("titulo", "").strip()
    abs_txt = (a.get("resumo") or "").strip()
    rev = a.get("revista", "").strip()
    ano = a.get("ano", "2026")
    prog = a.get("programa", "Metodologias e Bioimagem")
    pmc = a.get("pmc", "").strip()
    doi = a.get("doi", "").strip()
    pmid = a.get("pmid", "").strip()

    is_oa = bool(pmc) or a.get("tipo") == "preprint" or any(re.search(p, rev.lower()) for p in OPEN_ACCESS_PATTERNS)
    if doi:
        orig_url = f"https://doi.org/{doi}"
    elif pmc:
        orig_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/"
    else:
        orig_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    # Verificar se já está no cache com profundidade alta
    cached = cache.get(aid)
    if cached and len(cached.get("metodo_bancada", "")) > 250:
        analise = cached
    else:
        print(f"Consultando Gemini 3.8 Flash para: [{aid}] {tit[:50]}...")
        analise = analisar_com_gemini(aid, tit, abs_txt, rev, ano, prog)
        if analise:
            cache[aid] = analise
        else:
            return None

    prog_final = analise.get("programa_luchm") or prog
    met = analise.get("metodo_bancada") or a.get("metodo", "")
    imp = analise.get("implicacao_luchm") or a.get("implicacao", "")
    faisca = analise.get("faisca_lateral") or a.get("faisca_lateral", "")
    rac = analise.get("racional_bloco") or abs_txt
    res = analise.get("resultados_bloco") or "Principais resultados e cascatas moleculares reportados pelos autores."

    a["programa"] = prog_final
    a["metodo"] = met
    a["implicacao"] = imp
    a["faisca_lateral"] = faisca
    a["acesso_aberto"] = is_oa
    a["link_original"] = orig_url

    a["resumo_blocos"] = {
        "racional": rac,
        "metodologia": met,
        "resultados": res,
        "ancoragem_luchm": f"Articulado ao programa '{prog_final}' do LUCHM.",
        "implicacoes": imp,
        "faisca_lateral": faisca
    }
    return aid

def main():
    if not os.path.exists(EDICAO_FILE):
        print(f"Arquivo {EDICAO_FILE} não existe.")
        return

    with open(EDICAO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    artigos = data.get("colecao_artigos", {})
    cache = carregar_cache()

    print(f"Total de artigos a enriquecer com Gemini 3.8 Flash: {len(artigos)}")
    sucessos = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(processar_artigo, aid, a, cache): aid
            for aid, a in artigos.items()
        }
        for future in as_completed(futures):
            aid = futures[future]
            try:
                res = future.result()
                if res:
                    sucessos += 1
                    if sucessos % 10 == 0:
                        salvar_cache(cache)
                        print(f"Progresso: {sucessos}/{len(artigos)} enriquecidos...")
            except Exception as e:
                print(f"Erro processando {aid}: {e}")

    salvar_cache(cache)

    with open(EDICAO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Salvo {EDICAO_FILE} com {sucessos} artigos densamente enriquecidos.")

    # Re-embarcar no index.html
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()

        idx_start = html.find("const __EMBEDDED_DATA__ = {")
        if idx_start != -1:
            idx_end = html.find("};\n\n  function createLocalFallbackDb", idx_start)
            if idx_end != -1:
                artigos_list = list(artigos.values())
                json_str_antigo = html[idx_start + len("const __EMBEDDED_DATA__ = "): idx_end + 1]
                try:
                    embed_obj = json.loads(json_str_antigo)
                    embed_obj["artigos"] = artigos_list
                    novo_embed_json = json.dumps(embed_obj, ensure_ascii=False)
                    html = html[:idx_start + len("const __EMBEDDED_DATA__ = ")] + novo_embed_json + html[idx_end + 1:]
                    with open(INDEX_HTML, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"index.html re-embarcado com sucesso ({len(html)} bytes)!")
                except Exception as e:
                    print(f"Erro ao re-embarcar JSON no index.html: {e}")

if __name__ == "__main__":
    main()
