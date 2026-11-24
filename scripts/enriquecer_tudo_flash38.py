#!/usr/bin/env python3
"""
enriquecer_tudo_flash38.py — Enriquecimento Analítico Thread-Safe em 5 Blocos (LUCHM)

Melhorias estruturais (v2):
- Prioriza artigos `alta` (essenciais) e os melhores `media` da edição/quinzena (evitando
  desperdício de tempo e quota em ruído `baixa`, salvo se `--todos` for passado).
- Chaves JSON canônicas unificadas com `reclassificar.py` (`programa_luchm`, `racional`,
  `metodo_bancada`, `resultados`, `implicacao_luchm`, `faisca_lateral`).
- Escrita em `cache_flash38_artigos.json` protegida por `CACHE_LOCK` + substituição atômica.
- Verificação TLS padrão habilitada (sem `ssl._create_unverified_context()`).
- Ao finalizar novos enriquecimentos, dispara `reclassificar.py` automaticamente para
  sincronizar `conexoes_transversais`, `edicao_atual.json` e `edicao_embedded.js`.
"""

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import time
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

QUOTA_LOCK = threading.Lock()
CACHE_LOCK = threading.Lock()
QUOTA_EXHAUSTED = False

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDICAO_FILE = os.path.join(REPO_DIR, "data", "edicao_atual.json")
CACHE_FILE = os.path.join(REPO_DIR, "data", "cache_flash38_artigos.json")
RECLASS_SCRIPT = os.path.join(REPO_DIR, "scripts", "reclassificar.py")


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
MODEL_CANDIDATES = [
    os.environ.get("GEMINI_MODEL", "").strip(),
    "gemini-3.8-flash",
    "gemini-2.5-flash",
]
MODEL_CANDIDATES = [m for m in dict.fromkeys(MODEL_CANDIDATES) if m]


def criar_ssl_ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


SSL_CTX = criar_ssl_ctx()

PROGRAMAS_LUCHM = """
PROGRAMAS DE PESQUISA DO LUCHM (IBCCF/UFRJ - Prof. Fábio Gomes):
1. Malária Cerebral & Neuroinflamação (modelo murino C57BL/6J infectado com PbA; permeabilidade da barreira hematoencefálica; junções oclusivas claudina-5/occludina; astrócitos e micróglia; ferroptose endotelial e via MIF/CD74).
2. Repasto Sanguíneo HFHS & Metabolismo do Vetor (fêmeas de Aedes aegypti e Anopheles; alimentação com sangue de camundongos obesos em dieta hiperlipídica/hiperglicêmica; peroxidação lipídica mediada por hemo livre; estresse oxidativo no intestino médio; gotas lipídicas e ovogênese).
3. Imunidade de Vetores & RNAi (competência vetorial para Dengue, Zika, Chikungunya e Oropouche; vias de siRNA com Dicer-2 e Argonaute-2; imunidade antiviral e priming imune transgeracional).
4. Polifosfato Inorgânico & Acidocalcisomas (homeostase de bioenergética e armazenamento de cálcio/fósforo em protozoários parasitos e insetos; exopolifosfatase e polifosfato quinase; regulação de pH vacuolar).
5. Microscopia Eletrônica de Volume & Bioimagem (CENABIO/LUCHM; reconstrução tridimensional por FIB-SEM e SBF-SEM; sítios de contato de organelas / MCS; preservação ultraestrutural e protocolo OTO).
6. Biologia Celular de Plasmodium & Bloqueio de Transmissão (ciclo exoeritrocítico, oocinetos e esporozoítos; transição intestino-glândula salivar; antígenos Pfs25 e CSP).
7. Controle de Pragas & Bioinseticidas (Anticarsia gemmatalis e Spodoptera frugiperda; toxinas Cry de Bacillus thuringiensis; receptores ABCC2; membrana peritrófica e simbiontes).
"""


def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_cache_atomico(cache):
    with CACHE_LOCK:
        copia = dict(cache)
    tmp_path = CACHE_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(copia, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, CACHE_FILE)


def cache_valido(entry):
    if not isinstance(entry, dict):
        return False
    rac = entry.get("racional") or entry.get("racional_bloco") or ""
    met = entry.get("metodo_bancada") or ""
    res = entry.get("resultados") or entry.get("resultados_bloco") or ""
    return len(rac) > 80 and len(met) > 100 and len(res) > 80


def analisar_com_gemini(aid, titulo, abstract, revista, ano, programa_sugerido):
    global QUOTA_EXHAUSTED
    with QUOTA_LOCK:
        if QUOTA_EXHAUSTED or not API_KEY:
            return None

    prompt = f"""Você é o avaliador científico sênior do Laboratório de Ultraestrutura Celular Hertha Meyer (LUCHM/IBCCF/UFRJ), chefiado pelo Prof. Fábio Mendonça Gomes.

Analise o artigo científico abaixo e elabore uma síntese aprofundada, factual, técnica, densa e 100% em português com terminologia rigorosa de bancada.
REGRAS:
- NUNCA invente ensaios, organismos ou fármacos ausentes do abstract.
- NUNCA gere textos telegráficos. Cada bloco deve ter 3 a 5 frases completas e densas.

REFERÊNCIA DOS PROGRAMAS DO LABORATÓRIO:
{PROGRAMAS_LUCHM}

ARTIGO EM AVALIAÇÃO:
- ID: {aid}
- TÍTULO: {titulo}
- REVISTA: {revista} ({ano})
- ABSTRACT ORIGINAL: {abstract}
- PROGRAMA PRÉ-ASSOCIADO: {programa_sugerido}

Gere APENAS um objeto JSON com estas 6 chaves exatas:
{{
  "programa_luchm": "Nome exato de um dos 7 programas do LUCHM mais conectado a este estudo",
  "racional": "Parágrafo de 3 a 4 frases em português explicando a lacuna mecanística, o problema biológico e a hipótese central testada.",
  "metodo_bancada": "Parágrafo de 3 a 5 frases em português descrevendo o delineamento experimental real reportado no abstract (modelos, cepas, técnicas analíticas, concentrações e controles).",
  "resultados": "Parágrafo de 3 a 5 frases em português especificando os principais achados quantitativos, vias moleculares e fenótipos demonstrados.",
  "implicacao_luchm": "Parágrafo de 3 a 5 frases em português conectando concretamente os achados às perguntas experimentais ativas do LUCHM.",
  "faisca_lateral": "💡 Hipótese experimental testável de 2 a 3 frases propondo um ensaio concreto na bancada, insetário, biotério ou CENABIO do LUCHM."
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }

    for model_name in MODEL_CANDIDATES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, context=SSL_CTX, timeout=35) as resp:
                    res_data = json.loads(resp.read().decode())
                    cand = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(cand)
                    if isinstance(parsed, dict) and parsed.get("metodo_bancada"):
                        return parsed
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break  # Tenta próximo modelo candidato
                if e.code in (401, 402, 403):
                    with QUOTA_LOCK:
                        if not QUOTA_EXHAUSTED:
                            print(f"   ℹ️ API Gemini externa indisponível (HTTP {e.code}); preservando cache PT local.")
                        QUOTA_EXHAUSTED = True
                    return None
                time.sleep(1.5 * (attempt + 1))
            except Exception:
                time.sleep(1.5 * (attempt + 1))
    return None


def main():
    parser = argparse.ArgumentParser(description="Enriquece artigos prioritários com análise densa em 5 blocos.")
    parser.add_argument("--todos", action="store_true", help="Tenta enriquecer também artigos de baixa importância.")
    parser.add_argument("--limite", type=int, default=28, help="Máximo de artigos novos a consultar na API por execução.")
    args, _ = parser.parse_known_args()

    if not os.path.exists(EDICAO_FILE):
        print(f"Arquivo {EDICAO_FILE} não existe.")
        return

    with open(EDICAO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    artigos_dict = data.get("colecao_artigos", {})
    cache = carregar_cache()

    alvos = []
    ja_em_cache = 0
    for aid, a in artigos_dict.items():
        tit = (a.get("titulo") or "").strip()
        if re.match(r"^\s*(retraction|retracted|erratum|corrigendum)\b", tit.lower()):
            continue
        if cache_valido(cache.get(aid)):
            ja_em_cache += 1
            continue
        imp = a.get("importancia", "baixa")
        if not args.todos and imp == "baixa":
            continue
        alvos.append((aid, a))

    alvos.sort(key=lambda par: (0 if par[1].get("importancia") == "alta" else 1, -(par[1].get("score") or 0)))
    alvos = alvos[: args.limite]

    print(f"📚 Cache PT ativo: {ja_em_cache} artigos da edição já enriquecidos | Novos candidatos prioritários: {len(alvos)}")
    if not alvos or not API_KEY:
        if not API_KEY and alvos:
            print("   ℹ️ Sem GEMINI_API_KEY externa configurada; mantendo curadoria PT local / cache.")
        return

    novos_sucessos = 0

    def worker(item):
        aid, a = item
        abs_orig = (a.get("resumo_original") or a.get("resumo") or "").strip()
        analise = analisar_com_gemini(
            aid,
            a.get("titulo", ""),
            abs_orig,
            a.get("revista", ""),
            a.get("ano", "2026"),
            a.get("programa", ""),
        )
        if analise:
            normalizado = {
                "programa_luchm": (analise.get("programa_luchm") or a.get("programa") or "").strip(),
                "racional": (analise.get("racional") or analise.get("racional_bloco") or "").strip(),
                "metodo_bancada": (analise.get("metodo_bancada") or "").strip(),
                "resultados": (analise.get("resultados") or analise.get("resultados_bloco") or "").strip(),
                "implicacao_luchm": (analise.get("implicacao_luchm") or "").strip(),
                "faisca_lateral": (analise.get("faisca_lateral") or "").strip(),
            }
            with CACHE_LOCK:
                cache[aid] = normalizado
            return aid
        return None

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, item) for item in alvos]
        for fut in as_completed(futures):
            res_id = fut.result()
            if res_id:
                novos_sucessos += 1
                if novos_sucessos % 5 == 0:
                    salvar_cache_atomico(cache)
                    print(f"   ✓ Progresso: {novos_sucessos}/{len(alvos)} novos artigos enriquecidos...")

    if novos_sucessos > 0:
        salvar_cache_atomico(cache)
        print(f"✅ {novos_sucessos} novos artigos gravados em {CACHE_FILE}. Atualizando síntese transversal e edição...")
        subprocess.run([sys.executable, RECLASS_SCRIPT], cwd=REPO_DIR, check=True)


if __name__ == "__main__":
    main()
