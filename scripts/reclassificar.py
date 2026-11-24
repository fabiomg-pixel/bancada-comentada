#!/usr/bin/env python3
"""
reclassificar.py — Motor de Triagem Híbrida (v6 + LUCHM + High-Impact), Janela de 14 Dias & Vault

Melhorias estruturais (v2):
1. Funde os metadados curados pela revista oficial do Claude (`a["v6"]`: importância, score,
   resumo em PT, método e implicação) com ponderação real de periódicos `HIGH_IMPACT` e
   ancoragem estrita aos 7 programas oficiais do LUCHM.
2. Impede falsos positivos (`v6=baixa/0` nunca sobe para `alta` sem alvo central explícito;
   extratos foliares brutos sem mecanismo molecular ficam limitados a `media`).
3. Lê chaves canônicas e legadas de `data/cache_flash38_artigos.json` (`racional`/`racional_bloco`,
   `resultados`/`resultados_bloco`), eliminando a perda de blocos em português.
4. Mantém a janela rolante real de 14 dias (`DIAS_CIRCULACAO = 14`) + migração automática para
   `estagio: "vault"` de artigos `alta` ou marcados/catalogados em `data/interacoes.json`.
5. Gera `data/edicao_atual.json` (carregado via `fetch()` em HTTP/HTTPS) e `data/edicao_embedded.js`
   (fallback automático para abertura local via `file://`), deixando `index.html` enxuto e imutável.
"""

import datetime as dt
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(REPO_DIR, "data", "literature_capture_raw.json")
EDICAO_FILE = os.path.join(REPO_DIR, "data", "edicao_atual.json")
EMBEDDED_JS_FILE = os.path.join(REPO_DIR, "data", "edicao_embedded.js")
CULTURAL_FILE = os.path.join(REPO_DIR, "data", "radar_cultural.json")
CACHE_FILE = os.path.join(REPO_DIR, "data", "cache_flash38_artigos.json")
INTERACOES_FILE = os.path.join(REPO_DIR, "data", "interacoes.json")

DIAS_CIRCULACAO = 14

TIER1_JOURNALS = ["nature", "science", "cell"]
TIER2_JOURNALS = [
    "science advances", "sci adv", "current biology", "curr biol",
    "nature communications", "nat commun", "nature microbiology", "nature immunology",
    "cell host", "cell metabolism", "mol cell", "molecular cell", "immunity", "pnas",
    "proc natl acad sci", "embo", "trends", "annual review",
]
TIER3_JOURNALS = [
    "elife", "plos biology", "plos biol", "plos pathogens", "plos pathog",
    "plos neglected tropical diseases", "plos negl trop dis", "iscience",
    "communications biology", "commun biol", "nucleic acids res", "mbio",
    "cell reports", "cell rep", "emerg microbes infect", "parasites & vectors",
    "parasit vectors", "j invertebr pathol",
]

OPEN_ACCESS_PATTERNS = [
    r"malaria journal", r"frontiers", r"plos", r"nature communications", r"nat commun",
    r"science advances", r"sci adv", r"iscience", r"cell reports", r"medcomm", r"mbio",
    r"cureus", r"scientific reports", r"scientific data", r"bmc", r"elife",
    r"communications biology", r"commun biol", r"biorxiv", r"medrxiv",
    r"open access", r"jove", r"parasites & vectors", r"parasit vectors",
    r"emerg microbes infect", r"mol biomed",
]


def bonus_periodico(revista: str) -> int:
    r = (revista or "").lower().strip()
    if not r:
        return 0
    if r in TIER1_JOURNALS or any(re.match(rf"^{j}(\b|$)", r) for j in TIER1_JOURNALS) and "communications" not in r and "reports" not in r and "advances" not in r:
        return 12
    if any(j in r for j in TIER2_JOURNALS):
        return 8
    if any(j in r for j in TIER3_JOURNALS):
        return 5
    return 0


def eh_ingles_provavel(txt: str) -> bool:
    if not txt or len(txt) < 25:
        return False
    t = " " + txt.lower() + " "
    acentos = len(re.findall(r"[ãõçáéíóúêôâ]", t))
    en = sum(1 for w in [" the ", " and ", " with ", " that ", " were ", " showed ", " using ", " from ", " this ", " study "] if w in t)
    pt = sum(1 for w in [" de ", " do ", " da ", " para ", " com ", " que ", " por ", " no ", " na ", " como ", " após "] if w in t)
    if acentos == 0 and en >= 2 and pt == 0:
        return True
    return en >= 3 and en > pt


def separar_faisca_v6(texto_pt: str):
    """Extrai eventual sugestão iniciada por 💡 dentro do resumo/implicação da v6."""
    if not texto_pt or "💡" not in texto_pt:
        return (texto_pt or "").strip(), ""
    partes = texto_pt.split("💡", 1)
    corpo = partes[0].strip()
    faisca = "💡 " + partes[1].strip()
    return corpo, faisca


def mapear_programa_e_tema(txt: str, v6_tema: str):
    """Mapeia o artigo para um dos 7 programas canônicos do LUCHM e um dos 5 temas da UI."""
    has_mosquito = any(w in txt for w in ["aedes", "anopheles", "culex", "culicidae", "mosquito", "diptera", "blood meal", "midgut", "salivary"])
    has_plasmodium = "plasmodium" in txt or "malaria" in txt
    has_arbovirus = any(w in txt for w in ["dengue", "zika", "chikungunya", "oropouche", "mayaro", "alphavirus", "flavivirus", "arbovir", "west nile"])
    has_bt_pest = any(w in txt for w in ["bacillus thuringiensis", " bt ", "bt resistance", "cry1", "cry2", "vip3", "abcc2", "spodoptera", "anticarsia", "lepidoptera", "bioinsecticid"])
    has_polyp = any(w in txt for w in ["polyphosphate", "acidocalcisome", "exopolyphosphatase", "polyphosphate kinase", "ppx1", "ppk1"]) and "organophosphate" not in txt
    has_vem = any(w in txt for w in ["fib-sem", "sbf-sem", "serial block face", "volume electron", "cryo-et", "mitoem", "3d mitochondria", "membrane contact site", "organelle contact", "ribbon-vesicle"])

    if "cerebral malaria" in txt or (has_plasmodium and any(w in txt for w in ["blood-brain barrier", "cerebrospinal", "brain", "endothelial", "astrocyte", "microglia", "neuroinflamm"])):
        return "Malária Cerebral & Neuroinflamação", "cerebro"
    if has_bt_pest:
        return "Controle de Pragas & Bioinseticidas", "vetor"
    if has_polyp:
        return "Polifosfato Inorgânico & Acidocalcisomas", "metodos"
    if has_vem and not has_plasmodium:
        return "Microscopia Eletrônica de Volume & Bioimagem", "metodos"
    if has_plasmodium and any(w in txt for w in ["sporozoite", "ookinete", "oocyst", "gametocyte", "liver-stage", "transmission", "salivary", "pfs25", "csp", "ap2-", "mosquito-to-mouse"]):
        return "Biologia Celular de Plasmodium & Bloqueio de Transmissão", "ciclo"
    if has_plasmodium:
        return "Biologia Celular de Plasmodium & Bloqueio de Transmissão", "ciclo"
    if has_mosquito and any(w in txt for w in ["blood", "diet", "hfhs", "lipid", "heme", "hemopexin", "metaboli", "kinin", "sleep", "feeding", "rearing", "oviposition", "thermal", "timeless", "akh"]):
        return "Repasto Sanguíneo HFHS & Metabolismo do Vetor", "vetor"
    if has_arbovirus or (has_mosquito and any(w in txt for w in ["rnai", "dicer", "argonaute", "sirna", "competence", "antiviral", "immune", "hemocyte", "microbiome", "microbiota"])):
        return "Imunidade de Vetores & RNAi", "vetor"
    if "gut-brain" in txt or "interoception" in txt or "neuropeptide" in txt:
        return "Repasto Sanguíneo HFHS & Metabolismo do Vetor", "cerebro" if v6_tema == "cerebro" else "vetor"
    if "ferroptosis" in txt or "itaconate" in txt or "immunometabol" in txt:
        return "Malária Cerebral & Neuroinflamação" if "brain" in txt or "endothel" in txt else "Repasto Sanguíneo HFHS & Metabolismo do Vetor", "hospedeiro"

    tema_ui = v6_tema if v6_tema in ("cerebro", "vetor", "ciclo", "hospedeiro", "metodos") else "metodos"
    prog_default = {
        "cerebro": "Malária Cerebral & Neuroinflamação",
        "vetor": "Imunidade de Vetores & RNAi",
        "ciclo": "Biologia Celular de Plasmodium & Bloqueio de Transmissão",
        "hospedeiro": "Repasto Sanguíneo HFHS & Metabolismo do Vetor",
        "metodos": "Microscopia Eletrônica de Volume & Bioimagem",
    }[tema_ui]
    return prog_default, tema_ui


def classificar_artigo(a: dict):
    tit = (a.get("titulo") or "").strip()
    abs_orig = (a.get("resumo_original") or "").strip()
    v6 = a.get("v6") or {}
    v6_resumo_raw = (a.get("resumo_pt_v6") or v6.get("resumo") or "").strip()
    txt = f"{tit} {abs_orig} {v6_resumo_raw}".lower()
    journal = (a.get("revista") or "").strip()

    is_retraction = bool(re.match(r"^\s*(retraction|retracted|erratum|corrigendum|author correction|publisher correction)\b", tit.lower())) or "retraction notice" in txt

    has_core_organism = any(w in txt for w in [
        "plasmodium", "malaria", "aedes", "anopheles", "culex", "mosquito",
        "polyphosphate", "acidocalcisome", "bacillus thuringiensis", "spodoptera", "anticarsia",
        "oropouche", "chikungunya", "dengue", "zika", "drosophila", "caenorhabditis",
    ])

    offtopic_markers = [
        "stannous fluoride", "plaque biofilm", "feline heartworm", "dirofilaria",
        "epstein-barr", "melanoma", "tumorigenesis", "corpora amylacea",
        "water electrolyzer", "proton exchange membrane", "cyanobacterial bloom",
        "soil-plant", "banana peel", "silver nanoparticles", "preoperative opioid",
        "arthroplasty", "cardiomyopathy", "mycoplasma pneumoniae", "barite mineralization",
        "salinity acclimation", "testicular aging", "bovine mastitis", "bariatric surgery",
        "colorectal cancer", "intervertebral disc", "nanofibrous yarns", "solitary bees and wasps",
        "diabetes-related foot ulcer", "pulmonary arterial hypertension", "oral-brain axis",
        "ecmwf", "medium-range forecasts", "relative humidity verification",
        "osteotropic", "bone morphogenetic protein-2", "alzheimer", "parkinson", "huntington",
        "traditional chinese medicine", "insomnia", "covid-19", "listeria monocytogenes",
    ]
    is_offtopic = any(w in txt for w in offtopic_markers) and not any(
        k in txt for k in ["plasmodium", "malaria", "aedes", "anopheles", "polyphosphate", "acidocalcisome", "bacillus thuringiensis"]
    )
    is_crude_extract = ("ethnopharmacol" in journal.lower() or "leaf extract" in txt or "essential oil" in txt) and not any(
        k in txt for k in ["crystal structure", "crispr", "single-cell", "fib-sem"]
    )

    v6_imp = str(v6.get("importancia") or "").lower().strip()
    try:
        v6_score = float(v6.get("score") or 0)
    except (TypeError, ValueError):
        v6_score = 0.0
    v6_tema = str(v6.get("tema") or "").lower().strip()

    programa, tema = mapear_programa_e_tema(txt, v6_tema)
    j_bonus = bonus_periodico(journal)

    if is_retraction:
        return "baixa", "contexto", 5, "metodos", "Aviso Editorial / Retratação"
    if is_offtopic:
        return "baixa", "contexto", 25, tema, "Vigilância Bibliográfica Geral"

    # 1. Respeitar integralmente os destaques 'alta' da curadoria oficial v6
    if v6_imp == "alta" and not is_crude_extract:
        score = min(120, max(96, round(68 + v6_score * 0.45) + j_bonus))
        return "alta", "essencial", score, tema, programa

    # 2. Respeitar descartes 'baixa' (ou score 0) da v6 — não promover falsos positivos
    if v6_imp == "baixa" or (v6_imp == "" and v6_score == 0):
        # Exceção apenas se for artigo direto de Plasmodium/Aedes/Anopheles/PolyP/FIB-SEM em revista forte
        direct_luchm = any(k in txt for k in ["cerebral malaria", "acidocalcisome", "fib-sem", "sbf-sem"]) and j_bonus >= 5
        if direct_luchm:
            return "media", "contexto", 78 + j_bonus, tema, programa
        return "baixa", "contexto", max(30, min(58, round(35 + v6_score * 0.4))), tema, programa

    # 3. Extratos brutos / óleos essenciais ficam no máximo em 'media'
    if is_crude_extract:
        return "media", "contexto", min(76, round(55 + v6_score * 0.25)), tema, programa

    # 4. Artigos 'media' na v6 que tocam diretamente o núcleo experimental do LUCHM sobem para 'alta'
    strong_luchm_core = (
        ("cerebral malaria" in txt and any(w in txt for w in ["endothelial", "blood-brain barrier", "metabol", "cd8", "ripk1", "astrocyte", "microglia"]))
        or (("plasmodium" in txt or "malaria" in txt) and any(w in txt for w in [
            "mosquito-to-mouse", "ookinete", "sporozoite", "salivary", "gametocyte",
            "ap2-", "liver-stage", "transmission-blocking", "pvm", "hsp90",
        ]))
        or (("aedes" in txt or "anopheles" in txt) and any(w in txt for w in [
            "blood meal", "blood-derived", "hfhs", "hemopexin", "lipid droplet",
            "rnai", "dicer-2", "argonaute-2", "oropouche", "chikungunya", "dengue", "zika",
            "vector competence", "midgut microbiome",
        ]) and v6_score >= 45)
        or ("polyphosphate" in txt and any(w in txt for w in ["acidocalcisome", "plasmodium", "trypanosoma", "condensate", "compaction"]))
        or (any(w in txt for w in ["fib-sem", "sbf-sem", "volume electron microscopy", "ribbon-vesicle", "organelle contact"]) and j_bonus >= 5)
        or (any(w in txt for w in ["bt resistance", "abcc2", "cry1", "spodoptera", "anticarsia"]) and v6_score >= 35)
    )

    if strong_luchm_core:
        score = min(115, max(92, round(62 + v6_score * 0.45) + j_bonus))
        return "alta", "essencial", score, tema, programa

    if has_core_organism or v6_imp == "media":
        score = min(89, max(64, round(50 + v6_score * 0.42) + j_bonus))
        return "media", "contexto", score, tema, programa

    return "baixa", "contexto", 42, tema, "Vigilância Bibliográfica Geral"


def carregar_ids_protegidos():
    """IDs que nunca expiram (catalogados, anotados ou com sinais da equipe)."""
    protegidos = set()
    if not os.path.exists(INTERACOES_FILE):
        return protegidos
    try:
        with open(INTERACOES_FILE, encoding="utf-8") as f:
            inter = json.load(f)
        for cat in inter.get("catalogo") or []:
            protegidos.update(str(k) for k in (cat.get("itens") or {}).keys())
        for an in inter.get("anotacoes") or []:
            for k, v in (an.get("porArtigo") or {}).items():
                if (v or {}).get("itens"):
                    protegidos.add(str(k))
        for _, s in (inter.get("sinais") or {}).items():
            protegidos.update(str(k) for k in (s.get("itens") or {}).keys())
    except Exception:
        pass
    return protegidos


def construir_blocos_pt(tit, abs_orig, v6, resumo_pt_v6, programa, cached):
    """Monta os 5 blocos canônicos sempre priorizando português denso (cache -> v6 PT -> síntese PT)."""
    v6_res_limpo, faisca_v6 = separar_faisca_v6(resumo_pt_v6 or (v6.get("resumo") or ""))
    v6_imp_limpa, faisca_imp = separar_faisca_v6(v6.get("implicacao") or "")
    v6_met = (v6.get("metodo") or "").strip()

    rac_cache = ""
    met_cache = ""
    res_cache = ""
    imp_cache = ""
    fai_cache = ""

    if cached and isinstance(cached, dict):
        rac_cache = (cached.get("racional") or cached.get("racional_bloco") or "").strip()
        met_cache = (cached.get("metodo_bancada") or cached.get("metodologia") or "").strip()
        res_cache = (cached.get("resultados") or cached.get("resultados_bloco") or "").strip()
        imp_cache = (cached.get("implicacao_luchm") or cached.get("implicacoes") or "").strip()
        fai_cache = (cached.get("faisca_lateral") or "").strip()
        if cached.get("programa_luchm") and programa != "Aviso Editorial / Retratação":
            programa = cached["programa_luchm"].strip()

    racional = (
        rac_cache
        or (v6_res_limpo if v6_res_limpo and not eh_ingles_provavel(v6_res_limpo) else "")
        or f"Estudo voltado à caracterização mecanística e funcional abordada em «{tit}», no contexto de {programa}."
    )
    metodologia = (
        met_cache
        or (v6_met if v6_met and not eh_ingles_provavel(v6_met) else "")
        or f"Delineamento experimental detalhado no artigo original, articulado aos modelos analíticos acompanhados pelo programa de {programa}."
    )
    resultados = (
        res_cache
        or (v6_res_limpo if v6_res_limpo and not eh_ingles_provavel(v6_res_limpo) and rac_cache else "")
        or (f"Síntese da curadoria v6: {v6_res_limpo}" if v6_res_limpo and not eh_ingles_provavel(v6_res_limpo) else "Resultados quantitativos e relações funcionais descritos no resumo original (aba Resumo Original PubMed).")
    )
    implicacoes = (
        imp_cache
        or (v6_imp_limpa if v6_imp_limpa and not eh_ingles_provavel(v6_imp_limpa) else "")
        or f"Trabalho monitorado na frente de {programa} do LUCHM para cruzamento metodológico e conceitual."
    )
    faisca = (
        fai_cache
        or faisca_imp
        or faisca_v6
        or f"💡 Avaliar na reunião de grupo se os parâmetros experimentais deste estudo se aplicam aos protocolos ativos de {programa}."
    )
    if faisca and not faisca.startswith("💡"):
        faisca = "💡 " + faisca

    blocos = {
        "racional": racional,
        "metodologia": metodologia,
        "resultados": resultados,
        "ancoragem_luchm": f"Articulado diretamente ao programa '{programa}' do LUCHM.",
        "implicacoes": implicacoes,
        "faisca_lateral": faisca,
    }
    resumo_card_pt = v6_res_limpo if (v6_res_limpo and not eh_ingles_provavel(v6_res_limpo)) else racional
    return programa, metodologia, implicacoes, faisca, resumo_card_pt, blocos


def _rev_curta(rev):
    r = (rev or "").split(":")[0].replace("(preprint)", "").strip()
    return re.sub(r"^The\s+", "", r) or "PubMed"


def construir_conexoes_transversais(destaques_recentes, cultural):
    """Sintetiza 4 eixos transversais dinâmicos usando os achados/implicações em português já curados."""
    eixos = []
    por_frente = [
        ("Malária Cerebral, Coagulação & Imunometabolismo", [
            a for a in destaques_recentes
            if a.get("tema") in ("cerebro", "hospedeiro") or "Malária Cerebral" in (a.get("programa") or "")
        ]),
        ("Fisiologia do Vetor, Repasto Sanguíneo & Eixo Intestino-Cérebro", [
            a for a in destaques_recentes
            if a.get("tema") == "vetor" and "Controle de Pragas" not in (a.get("programa") or "")
        ]),
        ("Biologia Celular de Plasmodium & Bloqueio de Transmissão", [
            a for a in destaques_recentes
            if a.get("tema") == "ciclo" or "Plasmodium" in (a.get("programa") or "")
        ]),
        ("Bioinseticidas Bt, Bioimagem 3D & Horizonte Lateral", [
            a for a in destaques_recentes
            if a.get("tema") == "metodos" or "Controle de Pragas" in (a.get("programa") or "") or "Volume" in (a.get("programa") or "")
        ]),
    ]

    usados = set()
    ensaio = (cultural or {}).get("ensaio") or {}

    for rotulo_frente, candidatos in por_frente:
        disp = [a for a in candidatos if a["_id"] not in usados]
        if not disp:
            continue
        grp = disp[:2]
        for a in grp:
            usados.add(a["_id"])
        nomes = " & ".join(f"{_rev_curta(a.get('revista'))} ({a['_id']})" for a in grp)
        res_curto = (grp[0].get("resumo_blocos", {}).get("resultados") or grp[0].get("resumo") or grp[0].get("titulo") or "").strip()
        if len(res_curto) > 230:
            res_curto = res_curto[:227].rsplit(" ", 1)[0] + "…"
        ev = f"Em {nomes}: {res_curto}"
        eixo_obj = {
            "titulo": f"{len(eixos) + 1}. {rotulo_frente}",
            "evidencia": ev,
            "conexao_bancada": grp[0].get("implicacao") or "Cruzar parâmetros experimentais com os ensaios em curso no LUCHM.",
            "artigos_ref": [{"id": a["_id"], "rotulo": f"{_rev_curta(a.get('revista'))} · {a['_id']}"} for a in grp],
        }
        if "Horizonte Lateral" in rotulo_frente and ensaio.get("titulo"):
            eixo_obj["horizonte_lateral"] = "Bioeletricidade & Contactoma (Horizonte Lateral)"
        eixos.append(eixo_obj)

    # Completar até 4 eixos caso alguma frente estivesse vazia
    sobras = [a for a in destaques_recentes if a["_id"] not in usados]
    while len(eixos) < 4 and sobras:
        grp = sobras[:2]
        sobras = sobras[2:]
        nomes = " & ".join(f"{_rev_curta(a.get('revista'))} · {a['_id']}" for a in grp)
        res_curto = (grp[0].get("resumo_blocos", {}).get("racional") or grp[0].get("titulo") or "").strip()
        if len(res_curto) > 220:
            res_curto = res_curto[:217].rsplit(" ", 1)[0] + "…"
        add_hl = len(eixos) == 3 and ensaio.get("titulo") and not any(e.get("horizonte_lateral") for e in eixos)
        eixo_obj = {
            "titulo": f"{len(eixos) + 1}. {grp[0].get('programa', 'Convergência Experimental LUCHM')}",
            "evidencia": f"Em {nomes}: {res_curto}",
            "conexao_bancada": grp[0].get("implicacao") or "Integrar protocolo e alvos moleculares às linhas ativas do grupo.",
            "artigos_ref": [{"id": a["_id"], "rotulo": f"{_rev_curta(a.get('revista'))} · {a['_id']}"} for a in grp],
        }
        if add_hl:
            eixo_obj["horizonte_lateral"] = "Bioeletricidade & Contactoma (Horizonte Lateral)"
        eixos.append(eixo_obj)

    return eixos[:4]


def main():
    if not os.path.exists(RAW_FILE):
        print(f"Erro: {RAW_FILE} não encontrado.")
        sys.exit(1)

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    articles = raw_data.get("articles", [])
    if len(articles) < 5:
        print(f"⚠️ AVISO: Apenas {len(articles)} artigos brutos em {RAW_FILE}. Abortando para preservar acervo.")
        sys.exit(0)

    radar_cultural_data = {}
    if os.path.exists(CULTURAL_FILE):
        with open(CULTURAL_FILE, "r", encoding="utf-8") as f:
            radar_cultural_data = json.load(f)

    cache_enriquecido = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_enriquecido = json.load(f)
        except Exception:
            cache_enriquecido = {}

    acervo_anterior = {}
    if os.path.exists(EDICAO_FILE):
        try:
            with open(EDICAO_FILE, "r", encoding="utf-8") as f:
                ed_ant = json.load(f)
            col_ant = ed_ant.get("colecao_artigos") or {}
            if isinstance(col_ant, dict):
                acervo_anterior = col_ant
        except Exception:
            acervo_anterior = {}

    ids_protegidos = carregar_ids_protegidos()

    fuso_br = timezone(timedelta(hours=-3))
    hoje_iso = datetime.now(fuso_br).strftime("%Y-%m-%d")
    data_edicao = str(raw_data.get("data") or hoje_iso)
    data_ref = dt.date.fromisoformat(data_edicao)
    limite_circulacao = (data_ref - dt.timedelta(days=DIAS_CIRCULACAO)).isoformat()
    limite_recentes_pauta = (data_ref - dt.timedelta(days=3)).isoformat()

    reclassified = {}

    for a in articles:
        pmid = str(a.get("pmid") or a.get("doi") or "").strip()
        if not pmid:
            continue
        tit = (a.get("titulo") or "").strip()
        abs_orig = (a.get("resumo_original") or "").strip()
        resumo_pt_v6 = (a.get("resumo_pt_v6") or "").strip()
        v6 = a.get("v6") or {}
        journal = (a.get("revista") or "").strip()
        autores = (a.get("autores") or "Autores não informados").strip()
        ano = str(a.get("ano") or data_edicao[:4])
        doi = (a.get("doi") or "").strip()
        pmc_val = (a.get("pmc") or "").strip()
        entrou_em = str(a.get("entrou_em") or a.get("data_fonte") or data_edicao)
        visto_em = str(a.get("visto_em") or entrou_em)
        data_fonte = str(a.get("data_fonte") or entrou_em)

        importancia, prioridade, score, tema, programa = classificar_artigo(a)
        cached = cache_enriquecido.get(pmid)
        programa, metodo, implicacao, faisca, resumo_card_pt, blocos_resumo = construir_blocos_pt(
            tit, abs_orig, v6, resumo_pt_v6, programa, cached
        )

        is_preprint = a.get("fonte_captura") == "preprint" or any(x in journal.lower() for x in ("biorxiv", "medrxiv"))
        is_oa = bool(pmc_val) or is_preprint or any(re.search(p, journal.lower()) for p in OPEN_ACCESS_PATTERNS)

        if doi:
            link_orig = f"https://doi.org/{doi}"
        elif pmc_val:
            link_orig = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_val}/"
        elif pmid.isdigit():
            link_orig = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        else:
            link_orig = ""

        estagio = "vault" if entrou_em < limite_circulacao and (importancia == "alta" or pmid in ids_protegidos) else "circulacao"
        expira_em = (dt.date.fromisoformat(entrou_em) + dt.timedelta(days=DIAS_CIRCULACAO)).isoformat()

        reclassified[pmid] = {
            "_id": pmid,
            "titulo": tit,
            "autores": autores,
            "revista": journal,
            "ano": ano,
            "doi": doi,
            "pmid": pmid if pmid.isdigit() else "",
            "pmc": pmc_val,
            "tipo": "preprint" if is_preprint else "artigo",
            "acesso_aberto": is_oa,
            "link_original": link_orig,
            "resumo": resumo_card_pt,
            "resumo_original": (abs_orig if (importancia != "baixa" or visto_em == data_edicao) else "") or resumo_card_pt,
            "resumo_blocos": blocos_resumo,
            "metodo": metodo,
            "minutos": 25 if importancia == "alta" else 12,
            "tema": tema,
            "programa": programa,
            "importancia": importancia,
            "prioridade": prioridade,
            "implicacao": implicacao,
            "faisca_lateral": faisca,
            "score": score,
            "estagio": estagio,
            "expira_em": expira_em,
            "consulta": ", ".join(a.get("consultas", [])),
            "indicado_por": "Resumo da Literatura Científica v6 (LUCHM)",
            "fonte_captura": a.get("fonte_captura", "PubMed"),
            "data_fonte": data_fonte,
            "visto_em": visto_em,
            "entrou_em": entrou_em,
        }

    # Preservar no Vault artigos antigos de alta importância ou interagidos pela equipe
    vault_preservados = 0
    for ant_id, ant_art in acervo_anterior.items():
        if ant_id in reclassified:
            continue
        if ant_art.get("programa") == "Aviso Editorial / Retratação":
            continue
        imp_ant = ant_art.get("importancia")
        if imp_ant == "alta" or ant_id in ids_protegidos or ant_art.get("estagio") == "vault":
            copia = dict(ant_art)
            copia["estagio"] = "vault"
            reclassified[ant_id] = copia
            vault_preservados += 1

    # Ordenar priorizando: (1) em circulação vs vault, (2) edição mais recente no topo para a Pauta, (3) score
    colecao_artigos = sorted(
        reclassified.values(),
        key=lambda x: (
            1 if x.get("estagio") == "vault" else 0,
            0 if x.get("visto_em") == data_edicao else (1 if str(x.get("visto_em") or "") >= limite_recentes_pauta else 2),
            -(x.get("score") or 0),
        ),
    )

    artigos_do_dia = [a for a in colecao_artigos if a.get("visto_em") == data_edicao and a.get("estagio") != "vault"]
    alta_hoje = sum(1 for a in artigos_do_dia if a["importancia"] == "alta")
    media_hoje = sum(1 for a in artigos_do_dia if a["importancia"] == "media")
    baixa_hoje = sum(1 for a in artigos_do_dia if a["importancia"] == "baixa")

    # Seleção de destaques da Pauta Semanal ("o que ler antes da reunião"):
    # Prioriza os 'alta' do dia; se o dia tiver < 8 'alta' (ex.: 24/11 com 3 'alta'), completa com os melhores 'alta' das últimas 72h (23/11, 20/11)
    destaques_pool = sorted(
        [d for d in artigos_do_dia if d["importancia"] == "alta"],
        key=lambda x: -(x.get("score") or 0),
    )[:8]

    if len(destaques_pool) < 8:
        ids_ja = {d["_id"] for d in destaques_pool}
        recentes_alta = sorted(
            [
                d for d in colecao_artigos
                if d["importancia"] == "alta"
                and d["_id"] not in ids_ja
                and d.get("estagio") != "vault"
                and str(d.get("visto_em") or "") >= limite_recentes_pauta
            ],
            key=lambda x: (str(x.get("visto_em") or ""), x.get("score") or 0),
            reverse=True,
        )
        destaques_pool.extend(recentes_alta[: 8 - len(destaques_pool)])

    if len(destaques_pool) < 6:
        ids_ja = {d["_id"] for d in destaques_pool}
        extras_med = sorted(
            [d for d in artigos_do_dia if d["importancia"] == "media" and d["_id"] not in ids_ja],
            key=lambda x: -(x.get("score") or 0),
        )
        destaques_pool.extend(extras_med[: 6 - len(destaques_pool)])

    conexoes_geradas = construir_conexoes_transversais(destaques_pool, radar_cultural_data)
    inicio_semana = (data_ref - dt.timedelta(days=6)).isoformat()

    total_essenciais_circ = sum(1 for a in colecao_artigos if a.get("estagio") != "vault" and a.get("importancia") == "alta")
    lede_txt = (
        f"Curadoria híbrida v6 + LUCHM: {alta_hoje} essenciais na edição de {data_edicao} "
        f"({len(destaques_pool)} em destaque imediato para a reunião e {total_essenciais_circ} essenciais em circulação na quinzena)."
    )

    top_progs = []
    for d in destaques_pool:
        p_nome = d.get("programa", "")
        if p_nome and p_nome not in top_progs:
            top_progs.append(p_nome)

    resumo_dest_1 = "; ".join(
        f"{d.get('titulo', '').rstrip('.')} ({_rev_curta(d.get('revista'))}, {d['_id']})"
        for d in destaques_pool[:3]
    )
    resumo_dest_2 = "; ".join(
        f"{d.get('titulo', '').rstrip('.')} ({_rev_curta(d.get('revista'))}, {d['_id']})"
        for d in destaques_pool[3:6]
    )

    pauta_atual = {
        "semana": "Semana Corrente",
        "inicio": inicio_semana,
        "fim": data_edicao,
        "periodo": data_edicao,
        "titulo": "Edição Atual — Literatura Curada LUCHM (v6)",
        "lede": lede_txt,
        "panorama": [
            f"Na varredura mais recente ({len(artigos_do_dia)} artigos depositados em {data_edicao}; {len(colecao_artigos)} preservados na janela rolante de 14 dias + Vault), convergem achados em {', '.join(top_progs[:3]) or 'Malária, Vetores e Bioimagem'}, liderados por: {resumo_dest_1}.",
            f"Para discussão transversal na bancada e no clube de leitura desta semana, destacam-se em paralelo: {resumo_dest_2 or 'estudos complementares de fisiologia vetorial, imunometabolismo e bioimagem'}.",
        ],
        "conexoes_transversais": conexoes_geradas,
        "destaques": [
            {
                "artigo": d["_id"],
                "chamada": d["titulo"],
                "nota": f"Programa: {d.get('programa', '')} · Captura: {d.get('visto_em', data_edicao)} · Score LUCHM: {d.get('score')}",
            }
            for d in destaques_pool
        ],
        "vigiar": [
            f"{_rev_curta(d.get('revista'))} ({d['_id']}): {d.get('programa', '')} — {d.get('titulo', '')[:95]}"
            for d in destaques_pool[:4]
        ],
    }

    consultas_padrao = [
        "malaria_vetor", "vetores_mecanismo", "imunometabolismo",
        "polifosfato_ultraestrutura", "neuro_eixo", "lepidopteros_bt",
    ]

    # Construir histórico diário completo para a aba Radar Diário (com `_id` ISO exigido pelo frontend!)
    edicoes_radar = []
    for ed_meta in sorted(raw_data.get("edicoes_janela") or [{"data": data_edicao, "total": len(artigos_do_dia)}], key=lambda x: x["data"], reverse=True):
        d_iso = ed_meta["data"]
        arts_d = [x for x in colecao_artigos if (x.get("data_fonte") == d_iso or x.get("entrou_em") == d_iso)]
        edicoes_radar.append({
            "_id": d_iso,
            "data": d_iso,
            "total": ed_meta.get("total") or len(arts_d),
            "novos": len(arts_d),
            "alta": sum(1 for x in arts_d if x.get("importancia") == "alta"),
            "media": sum(1 for x in arts_d if x.get("importancia") == "media"),
            "baixa": sum(1 for x in arts_d if x.get("importancia") == "baixa"),
            "consultas": consultas_padrao,
            "fonte": "Espelho Oficial Resumo da Literatura Científica v6 (LUCHM)",
        })

    radar_edicao_dia = edicoes_radar[0] if edicoes_radar else {
        "_id": data_edicao,
        "data": data_edicao,
        "total": len(artigos_do_dia),
        "novos": len(artigos_do_dia),
        "ja_vistos": 0,
        "alta": alta_hoje,
        "media": media_hoje,
        "baixa": baixa_hoje,
        "consultas": consultas_padrao,
        "janela_edat": f"janela rolante {DIAS_CIRCULACAO}d",
        "fonte": "Espelho Oficial Resumo da Literatura Científica v6 (LUCHM)",
    }

    serie_totais = [e["total"] for e in reversed(edicoes_radar[:7])] or [len(artigos_do_dia)]
    serie_rotulos = [e["data"][5:] for e in reversed(edicoes_radar[:7])] or [data_edicao[5:]]

    indicadores = [
        {
            "_id": "ind-circulacao-v6",
            "painel": "bancada",
            "ordem": 1,
            "rotulo": "Artigos na Quinzena Ativa (v6)",
            "valor": sum(1 for a in colecao_artigos if a.get("estagio") != "vault"),
            "unidade": "artigos",
            "delta": len(artigos_do_dia),
            "delta_rotulo": f"capturados em {data_edicao}",
            "serie": serie_totais,
            "serie_rotulos": serie_rotulos,
            "meta": 50,
            "estado": "ok",
            "fonte": "Espelho v6 LUCHM",
            "atualizado": data_edicao,
            "hero": True,
        },
        {
            "_id": "ind-essenciais-quinzena",
            "painel": "bancada",
            "ordem": 2,
            "rotulo": "Estudos Essenciais (Alta Prioridade)",
            "valor": total_essenciais_circ,
            "unidade": "essenciais",
            "delta": alta_hoje,
            "delta_rotulo": f"novos hoje ({data_edicao})",
            "serie": [e["alta"] for e in reversed(edicoes_radar[:7])],
            "serie_rotulos": serie_rotulos,
            "meta": 15,
            "estado": "ok",
            "fonte": "Triagem Híbrida v6 + LUCHM",
            "atualizado": data_edicao,
            "hero": False,
        },
        {
            "_id": "ind-cobertura-pt",
            "painel": "bancada",
            "ordem": 3,
            "rotulo": "Fichas Densas no Cache PT",
            "valor": len(cache_enriquecido),
            "unidade": "fichas",
            "delta": sum(1 for d in destaques_pool if d["_id"] in cache_enriquecido),
            "delta_rotulo": f"de {len(destaques_pool)} destaques em cache",
            "serie": [max(0, len(cache_enriquecido) - 12), max(0, len(cache_enriquecido) - 5), len(cache_enriquecido)],
            "serie_rotulos": ["ant", "ontem", "atual"],
            "meta": 200,
            "estado": "ok",
            "fonte": "Cache Analítico LUCHM",
            "atualizado": data_edicao,
            "hero": False,
        },
    ]

    sistema_radar = {
        "ultima_varredura": datetime.now(fuso_br).isoformat(),
        "consultas": consultas_padrao,
        "novos_hoje": len(artigos_do_dia),
        "fonte": "Espelho Oficial v6 (claude.ai -> GitHub)",
    }
    sistema_painel = {
        "atualizado": datetime.now(fuso_br).isoformat(),
        "fonte": "Antigravity Lab Management (v6)",
    }

    edicao_data = {
        "colecao_artigos": {d["_id"]: d for d in colecao_artigos},
        "radar_cultural": radar_cultural_data,
        "pauta": {"atual": pauta_atual},
        "clube": [],
        "radar": edicoes_radar,
        "indicadores": indicadores,
        "catalogo": [],
        "anotacoes": [],
        "sistema": {
            "radar": sistema_radar,
            "painel": sistema_painel,
        },
        "radar_edicao_dia": radar_edicao_dia,
        "sistema_radar": sistema_radar,
        "edicao": radar_edicao_dia,
    }

    tmp_ed = EDICAO_FILE + ".tmp"
    with open(tmp_ed, "w", encoding="utf-8") as f:
        json.dump(edicao_data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp_ed, EDICAO_FILE)

    # Gerar fallback JS externo para funcionamento 100% offline via file:// sem inchar index.html
    tmp_js = EMBEDDED_JS_FILE + ".tmp"
    with open(tmp_js, "w", encoding="utf-8") as f:
        f.write("window.__EMBEDDED_DATA__ = ")
        json.dump(edicao_data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    os.replace(tmp_js, EMBEDDED_JS_FILE)

    print(
        f"✅ Edição {data_edicao} salva: hoje={len(artigos_do_dia)} ({alta_hoje} Alta, {media_hoje} Média, {baixa_hoje} Baixa) "
        f"| Quinzena={len(colecao_artigos)} ({vault_preservados} no Vault) | Destaques Pauta={len(destaques_pool)}."
    )


if __name__ == "__main__":
    main()
