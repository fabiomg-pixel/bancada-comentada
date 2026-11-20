#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_podcast_28min.py — Motor de Áudio Neural Jornalístico v3 (Stork Cast — LUCHM/IBCCF/UFRJ)

Arquitetura de Voz Única (Audio-First Copywriting + Chunking de 3.500 caracteres):
- Voz oficial: pt-BR-AntonioNeural (via edge-tts) com velocidade --rate=+3% (ritmo de rádio jornalismo).
- Sem alternância picotada entre personagens e sem inserção de silêncios artificiais.
- Fatiamento inteligente em blocos de até 3.500 caracteres cortando estritamente em quebras de parágrafo (\n\n).
- Concatenação binária direta dos fluxos MP3 gerados pelo edge-tts (contínuo e sem estalos).
- Resiliência em camadas:
    * Nível 1 (Principal): edge-tts com pt-BR-AntonioNeural (+3%).
    * Nível 2 (Fallback Local Offline): macOS `say -v Luciana` convertido para MP3 mono via ffmpeg.
    * Nível 3 (Navegador): botão "Ouvir com voz do navegador" (Web Speech API, pt-BR, rate 1.03) no index.html.
- Sincronização automática:
    1. Repositório/Web: audio/briefing_atual.mp3, audio/briefing_atual.txt e cópias datadas.
    2. Mac do Fábio: ~/Downloads/LUCHM_Podcast_Comutacao_{data}.mp3 e ~/Downloads/LUCHM_Podcast_Transcricao_{data}.txt.
    3. Google Drive: stork-podcast/episodes/stork-cast-{data}-profundo-28min.mp3.
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess
import shutil
import time
import re
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_DIR, "data")
AUDIO_DIR = os.path.join(REPO_DIR, "audio")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "audio"), exist_ok=True)

VOZ_PRINCIPAL = "pt-BR-AntonioNeural"
TAXA_PRINCIPAL = "+3%"
LIMITE_CHUNK_CHARS = 3500

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def formatar_data_extenso(iso_date):
    try:
        parts = str(iso_date).split("-")
        ano = parts[0]
        mes_idx = int(parts[1]) - 1
        dia = int(parts[2])
        return f"{dia} de {MESES_PT[mes_idx]} de {ano}"
    except Exception:
        return str(iso_date)


def carregar_dados_edicao():
    caminho = os.path.join(DATA_DIR, "edicao_atual.json")
    if not os.path.exists(caminho):
        print(f"⚠️ Arquivo {caminho} não encontrado.")
        return {}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_radar_cultural():
    caminho = os.path.join(DATA_DIR, "radar_cultural.json")
    if not os.path.exists(caminho):
        return {}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def extrair_artigos_dict(edicao_data):
    colecao = edicao_data.get("colecao_artigos", {})
    if isinstance(colecao, dict):
        return list(colecao.values())
    if isinstance(colecao, list):
        return colecao
    artigos = edicao_data.get("artigos", [])
    return artigos if isinstance(artigos, list) else []


def eh_texto_ingles(txt):
    if not txt or len(txt) < 20:
        return False
    t = " " + txt.lower() + " "
    acentos_pt = len(re.findall(r"[ãõçáéíóúêôâ]", t))
    marcadores_en = sum(
        1 for w in [
            " the ", " and ", " of ", " with ", " that ", " from ", " were ", " was ",
            " is ", " are ", " for ", " this ", " these ", " showed ", " using ",
            " results ", " however ", " between ", " although ", " review ",
            " summarizes ", " study ", " which ", " have been ", " current ",
        ] if w in t
    )
    marcadores_pt = sum(
        1 for w in [
            " de ", " do ", " da ", " dos ", " das ", " em ", " para ", " com ",
            " que ", " por ", " no ", " na ", " nos ", " nas ", " como ", " são ",
            " foi ", " uma ", " um ", " sobre ", " enquanto ", " além ",
        ] if w in t
    )
    if acentos_pt == 0 and marcadores_en >= 2 and marcadores_pt == 0:
        return True
    return marcadores_en >= 3 and marcadores_en > marcadores_pt


def eh_artigo_fora_de_escopo(artigo):
    tit = (artigo.get("titulo") or "").lower()
    if re.match(r"^\s*(retraction|retracted|erratum|corrigendum)\b", tit) or "retraction notice" in tit:
        return True
    txt = f"{tit} {(artigo.get('resumo') or '')[:500]}".lower()
    ruidos = [
        "huntington", "insomnia", "insônia", "traditional chinese medicine",
        "alzheimer", "parkinson", "glioblastoma", "prostate cancer", "breast cancer",
        "water electrolyzer", "proton exchange membrane", "cyanobacterial",
        "soil-plant", "opioid", "arthroplasty", "numb paradox",
        "mullins-sekerka", "barite mineralization", "mineralization at gas-liquid",
        "salinity acclimation", "testicular aging", "anthocyanins",
        "bovine mastitis", "bariatric surgery", "colorectal cancer",
        "intervertebral disc", "nanofibrous yarns", "solitary bees and wasps",
        "stannous fluoride", "plaque biofilm", "feline heartworm",
        "epstein-barr", "melanoma", "corpora amylacea", "ribosome-associated vesicles",
    ]
    if any(r in txt for r in ruidos) and not any(
        k in txt for k in ["plasmodium", "malaria", "anopheles", "aedes", "mosquito", "polyphosphate"]
    ):
        return True
    return False


def extrair_bloco(artigo, chave, default=""):
    if not isinstance(artigo, dict):
        return default
    rb = artigo.get("resumo_blocos", {})
    cand = ""
    if isinstance(rb, dict) and rb.get(chave):
        cand = str(rb.get(chave)).strip()
    elif artigo.get(chave):
        cand = str(artigo.get(chave)).strip()
    if cand and not eh_texto_ingles(cand) and "Trabalho de contexto biológico complementar" not in cand:
        return cand
    return default


def _tem_blocos_pt(art):
    rb = art.get("resumo_blocos") or {}
    if not isinstance(rb, dict):
        return False
    rac = str(rb.get("racional") or "").strip()
    met = str(rb.get("metodologia") or "").strip()
    res = str(rb.get("resultados") or "").strip()
    return (
        len(rac) > 40 and not eh_texto_ingles(rac)
        and len(met) > 40 and not eh_texto_ingles(met) and not met.startswith("Delineamento experimental descrito")
        and len(res) > 40 and not eh_texto_ingles(res)
    )


def _limpar_emojis(txt):
    t = str(txt or "").strip()
    t = re.sub(r"^[💡🎯🔬⚙️🧬🦟🧠📊🧭📌🎙️📋\s]+", "", t)
    return t


def _garantir_ponto(txt):
    t = str(txt or "").strip()
    if not t:
        return ""
    if t[-1] in ".!?":
        return t
    return t + "."


def _min_ini(txt):
    t = str(txt or "").strip()
    if not t:
        return t
    if len(t) >= 2 and (t[1].isupper() or t[1] in "-0123456789"):
        return t
    return t[0].lower() + t[1:]


def resumir_revista_id(artigo):
    rev = (artigo.get("revista") or "Periódico indexado").split(":")[0].strip()
    rev = re.sub(r"^The\s+", "", rev)
    ident = str(artigo.get("pmid") or artigo.get("_id") or "").strip()
    if ident.startswith("10."):
        return f"{rev}, DOI {ident}"
    if ident:
        return f"{rev}, PMID {ident}"
    return rev


def formatar_lista_pt(itens, limite=4):
    itens = [str(x).strip() for x in itens if str(x).strip()][:limite]
    if not itens:
        return ""
    if len(itens) == 1:
        return itens[0]
    return ", ".join(itens[:-1]) + " e " + itens[-1]


def _blocos_seguros(art):
    prog = art.get("programa") or "Vigilância Científica LUCHM"
    rac = extrair_bloco(art, "racional", f"Investigação voltada a mecanismos centrais ligados ao eixo {prog}.")
    met = extrair_bloco(art, "metodologia", f"Delineamento experimental conduzido dentro da frente de {prog}.")
    res = extrair_bloco(art, "resultados", f"Os resultados detalham alterações quantitativas relevantes para o modelo experimental avaliado.")
    imp = extrair_bloco(art, "implicacoes", f"Dialoga diretamente com a agenda experimental do programa {prog} no LUCHM.")
    faisca = _limpar_emojis(extrair_bloco(art, "faisca_lateral", ""))
    return rac, met, res, imp, faisca


def _formatar_materia_audio_first(art, inclui_faisca=True):
    """Formata um artigo no padrão Audio-First:
    Editoria com ponto final -> Periódico e título com ponto final ->
    3 parágrafos contínuos (contexto, método, achados) -> Arremate 'Por que importa na bancada:'.
    """
    prog = _garantir_ponto(art.get("programa") or "Vigilância Científica")
    rev_id = _garantir_ponto(resumir_revista_id(art))
    tit = _garantir_ponto(art.get("titulo") or "Estudo selecionado da edição")
    rac, met, res, imp, faisca = _blocos_seguros(art)

    cabecalho = f"{prog} {rev_id} {tit}"
    p1 = _garantir_ponto(rac)
    p2 = f"Na bancada e no desenho experimental, {_min_ini(_garantir_ponto(met))}"
    p3 = _garantir_ponto(res)

    arremate = f"Por que importa na bancada: {_garantir_ponto(imp)}"
    if inclui_faisca and faisca:
        arremate += f" Próximo passo no LUCHM: {_garantir_ponto(faisca)}"

    return [cabecalho, p1, p2, p3, arremate]


def construir_roteiro_narrado(edicao_data, cultural_data, data_edicao):
    """Gera o roteiro contínuo em voz única (lista de parágrafos separados por \\n\\n)."""
    artigos = extrair_artigos_dict(edicao_data)
    total_artigos = len(artigos)
    altas = sum(1 for a in artigos if a.get("importancia") == "alta")
    medias = sum(1 for a in artigos if a.get("importancia") == "media")
    data_extenso = formatar_data_extenso(data_edicao)
    conexoes = (edicao_data.get("pauta", {}).get("atual", {}) or {}).get("conexoes_transversais", [])

    candidatos = [
        a for a in artigos
        if not eh_artigo_fora_de_escopo(a)
        and a.get("importancia") in ("alta", "media")
    ]
    candidatos.sort(
        key=lambda x: (
            0 if _tem_blocos_pt(x) else 1,
            0 if x.get("importancia") == "alta" else 1,
            -(x.get("score") or 0),
        )
    )

    usados = set()
    grupo_plasmodium = []
    grupo_vetores = []
    grupo_fronteira_metodos = []

    for a in candidatos:
        aid = str(a.get("_id") or a.get("pmid") or "")
        tema = (a.get("tema") or "").lower()
        prog = (a.get("programa") or "").lower()
        blob = f"{a.get('titulo', '')} {prog}".lower()

        if tema in ("ciclo", "hospedeiro") or any(
            k in blob for k in ["plasmodium", "malaria", "pantothenate", "cholesterol", "gametocyte", "pfht1", "rodent malaria"]
        ):
            if len(grupo_plasmodium) < 4:
                grupo_plasmodium.append(a)
                usados.add(aid)
        elif tema == "vetor":
            if len(grupo_vetores) < 4:
                grupo_vetores.append(a)
                usados.add(aid)

    for a in candidatos:
        aid = str(a.get("_id") or a.get("pmid") or "")
        if aid in usados:
            continue
        if len(grupo_fronteira_metodos) < 3:
            grupo_fronteira_metodos.append(a)
            usados.add(aid)

    while len(grupo_plasmodium) < 2 and grupo_fronteira_metodos:
        grupo_plasmodium.append(grupo_fronteira_metodos.pop())
    while len(grupo_vetores) < 2 and grupo_fronteira_metodos:
        grupo_vetores.append(grupo_fronteira_metodos.pop())

    con_titulos = [re.sub(r"^\d+\.\s*", "", str(c.get("titulo") or "")).strip() for c in conexoes[:4] if c.get("titulo")]
    destaques_rev = formatar_lista_pt(
        list(dict.fromkeys(re.sub(r"^The\s+", "", (a.get("revista") or "").split(":")[0].strip()) for a in candidatos[:6] if a.get("revista"))),
        limite=4,
    )

    # Abertura direta (< 25 segundos) com data por extenso
    abertura = [
        f"Bancada Comentada do LUCHM. Edição de {data_extenso}.",
        (
            f"Na análise de hoje triamos {total_artigos} publicações recentes e identificamos {altas} estudos prioritários "
            f"e {medias} de acompanhamento em {destaques_rev or 'periódicos indexados'}, articulados em "
            f"{formatar_lista_pt(con_titulos, 4) or 'biologia de Plasmodium, vetores e métodos de bancada'}. "
            f"Vamos direto ao primeiro artigo."
        ),
    ]

    # Bloco Horizonte Lateral (dinâmico de data/radar_cultural.json)
    ensaio = cultural_data.get("ensaio", {})
    titulo_ensaio = ensaio.get("titulo", "Física Oculta da Transmissão")
    ponto_cego = ensaio.get("subtitulo") or ensaio.get("ponto_cego") or ""
    pesquisadores = cultural_data.get("grandes_pesquisadores", [])
    temas_exp = cultural_data.get("temas_expansao", [])
    tecnicas = cultural_data.get("tecnicas_emergentes", [])

    bloco_hl = ["Passamos agora ao bloco Horizonte Lateral. Pontos cegos conceituais e técnicas fora da linha direta da parasitologia."]
    bloco_hl.append(f"Ensaio da edição mensal. {_garantir_ponto(titulo_ensaio)} {_garantir_ponto(ponto_cego)}")
    if len(pesquisadores) >= 2:
        p1, p2 = pesquisadores[0], pesquisadores[1]
        p1_conc = p1.get("conceito_chave") or p1.get("por_que_nao_obvia") or ""
        p1_imp = p1.get("por_que_importa_luchm") or p1.get("intersecao_luchm") or ""
        p2_conc = p2.get("conceito_chave") or p2.get("por_que_nao_obvia") or ""
        p2_imp = p2.get("por_que_importa_luchm") or p2.get("intersecao_luchm") or ""
        bloco_hl.append(
            f"Dois pesquisadores de referência lateral ancoram esta edição. "
            f"{p1.get('nome', '')}, de {p1.get('instituicao', '')}, destaca {_min_ini(_garantir_ponto(p1_conc))} {_garantir_ponto(p1_imp)}"
        )
        bloco_hl.append(
            f"Em complemento, {p2.get('nome', '')}, de {p2.get('instituicao', '')}, demonstra {_min_ini(_garantir_ponto(p2_conc))} {_garantir_ponto(p2_imp)}"
        )
    if len(temas_exp) >= 2:
        t1, t2 = temas_exp[0], temas_exp[1]
        bloco_hl.append(
            f"Nos temas em expansão lateral, destacamos {_garantir_ponto(t1.get('tema') or t1.get('titulo') or '')} "
            f"{_garantir_ponto(t1.get('o_que_e', ''))} "
            f"Ao lado de {_garantir_ponto(t2.get('tema') or t2.get('titulo') or '')} "
            f"{_garantir_ponto(t2.get('o_que_e', ''))}"
        )
    if len(tecnicas) >= 2:
        tc1, tc2 = tecnicas[0], tecnicas[1]
        bloco_hl.append(
            f"Por que importa na bancada: as técnicas emergentes da edição — "
            f"{tc1.get('tecnica') or tc1.get('titulo') or ''} e {tc2.get('tecnica') or tc2.get('titulo') or ''} — "
            f"{_min_ini(_garantir_ponto(tc1.get('aplicacao_luchm') or ''))}"
        )

    # Fechamento com 3 diretrizes acionáveis
    def _montar_fechamento(top3):
        out = ["Encerramos o boletim com três diretrizes objetivas para a bancada do LUCHM."]
        for idx_f, art in enumerate(top3, start=1):
            _, _, _, imp, faisca = _blocos_seguros(art)
            rev_id = resumir_revista_id(art)
            acao = faisca or imp
            out.append(f"Diretriz número {idx_f}, baseada em {rev_id}. {_garantir_ponto(acao)}")
        out.append(
            f"Todas as fichas detalhadas em cinco blocos, PMIDs clicáveis e os quatro eixos transversais desta edição de "
            f"{data_extenso} estão disponíveis na aba Pauta da Bancada Comentada. Boa jornada experimental no LUCHM."
        )
        return out

    def _montar_corpo(gp, gv, gm, incl_faisca=True):
        parags = list(abertura)

        if gp:
            parags.append("Iniciamos pelo bloco de biologia celular de Plasmodium e bloqueio de transmissão.")
            for art in gp:
                parags.extend(_formatar_materia_audio_first(art, inclui_faisca=incl_faisca))

        if gv:
            parags.append("Passamos agora ao bloco de vetores, fisiologia do repasto sanguíneo e arboviroses.")
            for art in gv:
                parags.extend(_formatar_materia_audio_first(art, inclui_faisca=incl_faisca))

        if gm:
            parags.append("Avançamos para o bloco de barreira endotelial, ultraestrutura e métodos de fronteira.")
            for art in gm:
                parags.extend(_formatar_materia_audio_first(art, inclui_faisca=incl_faisca))

        parags.extend(bloco_hl)
        top3 = (gp + gm + gv)[:3]
        parags.extend(_montar_fechamento(top3))
        return parags

    # Orçamento adaptativo: mira 3.100 a 3.750 palavras (~21 a 26 min em +3%)
    opcoes_cota = [
        (4, 4, 3, True),
        (4, 3, 2, True),
        (3, 3, 2, True),
        (3, 3, 2, False),
        (3, 2, 2, True),
        (3, 2, 2, False),
        (2, 2, 2, True),
    ]
    paragrafos = _montar_corpo(grupo_plasmodium[:3], grupo_vetores[:3], grupo_fronteira_metodos[:2], True)
    for cp, cv, cm, inc_f in opcoes_cota:
        cand = _montar_corpo(
            grupo_plasmodium[:cp],
            grupo_vetores[:cv],
            grupo_fronteira_metodos[:cm],
            incl_faisca=inc_f,
        )
        n_words = sum(len(p.split()) for p in cand)
        if n_words <= 3750:
            paragrafos = cand
            break
    else:
        paragrafos = cand

    return "\n\n".join(p.strip() for p in paragrafos if p and p.strip())


def chunking_por_paragrafos(roteiro_texto: str, limite_chars: int = LIMITE_CHUNK_CHARS):
    """Fatia o texto em blocos de até limite_chars cortando estritamente em quebras duplas de linha (\\n\\n)."""
    blocos = []
    atual = []
    tamanho_atual = 0
    for paragrafo in roteiro_texto.split("\n\n"):
        paragrafo = paragrafo.strip()
        if not paragrafo:
            continue
        extra = len(paragrafo) + (2 if atual else 0)
        if tamanho_atual + extra > limite_chars and atual:
            blocos.append("\n\n".join(atual))
            atual = [paragrafo]
            tamanho_atual = len(paragrafo)
        else:
            atual.append(paragrafo)
            tamanho_atual += extra
    if atual:
        blocos.append("\n\n".join(atual))
    return blocos


async def gerar_audio_jornalistico(
    roteiro_texto: str,
    arquivo_saida_mp3: str,
    voz: str = VOZ_PRINCIPAL,
    taxa: str = TAXA_PRINCIPAL,
    limite_chars: int = LIMITE_CHUNK_CHARS,
) -> bool:
    """Nível 1: edge-tts com pt-BR-AntonioNeural (+3%), chunking <= 3.500 chars e concatenação binária direta.
    Nível 2 (Fallback local offline): macOS `say -v Luciana` convertido via ffmpeg se o edge-tts falhar.
    """
    import edge_tts

    os.makedirs(os.path.dirname(os.path.abspath(arquivo_saida_mp3)), exist_ok=True)
    blocos = chunking_por_paragrafos(roteiro_texto, limite_chars=limite_chars)
    print(f"🎙️ Síntese Neural Contínua ({voz}, rate={taxa}): {len(blocos)} blocos (≤ {limite_chars} chars cada)...")

    partes_mp3 = []
    sucesso = True

    for i, bloco in enumerate(blocos):
        mp3_part = f"{arquivo_saida_mp3}.part{i:02d}.mp3"
        if os.path.exists(mp3_part) and os.path.getsize(mp3_part) > 10000:
            partes_mp3.append(mp3_part)
            print(f"   ⚡ Bloco [{i + 1:02d}/{len(blocos):02d}]: reutilizado do cache parcial ({os.path.getsize(mp3_part):,} bytes)")
            continue
        t0 = time.time()
        ok_part = False
        for tentativa in range(4):
            try:
                com = edge_tts.Communicate(bloco, voz, rate=taxa, pitch="+0Hz")
                await asyncio.wait_for(com.save(mp3_part), timeout=90)
                if os.path.exists(mp3_part) and os.path.getsize(mp3_part) > 1000:
                    ok_part = True
                    break
            except Exception as e:
                if os.path.exists(mp3_part):
                    os.remove(mp3_part)
                print(f"   ⚠️ Tentativa {tentativa + 1} falhou no bloco {i + 1}/{len(blocos)}: {type(e).__name__}: {e}")
                await asyncio.sleep(1.5 * (tentativa + 1))

        if not ok_part:
            sucesso = False
            break

        dt = time.time() - t0
        partes_mp3.append(mp3_part)
        print(f"   ✓ Bloco [{i + 1:02d}/{len(blocos):02d}]: {len(bloco)} chars ({len(bloco.split())} palavras) em {dt:.1f}s")

    if sucesso and partes_mp3:
        with open(arquivo_saida_mp3, "wb") as fout:
            for p in partes_mp3:
                with open(p, "rb") as fin:
                    fout.write(fin.read())
                os.remove(p)
        print(f"   ✅ Concatenação binária direta concluída ({os.path.getsize(arquivo_saida_mp3):,} bytes).")
        return True

    # Limpeza de parciais em caso de falha no Nível 1
    for p in partes_mp3:
        if os.path.exists(p):
            os.remove(p)

    # Nível 2: Fallback local offline (macOS say -v Luciana -> MP3 mono)
    if shutil.which("say") and shutil.which("ffmpeg"):
        print("   🔄 Recorrendo ao Nível 2 (Fallback local offline: say -v Luciana + ffmpeg)...")
        aiff_path = f"{arquivo_saida_mp3}.fallback.aiff"
        try:
            subprocess.run(["say", "-v", "Luciana", "-r", "195", "-o", aiff_path, roteiro_texto], check=True)
            subprocess.run(
                ["ffmpeg", "-y", "-i", aiff_path, "-ac", "1", "-b:a", "48k", arquivo_saida_mp3],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return os.path.exists(arquivo_saida_mp3) and os.path.getsize(arquivo_saida_mp3) > 1000
        finally:
            if os.path.exists(aiff_path):
                os.remove(aiff_path)

    return False


async def main():
    parser = argparse.ArgumentParser(description="Motor de Áudio Neural Jornalístico LUCHM v3 (Voz Única)")
    parser.add_argument("--somente-texto", action="store_true", help="Gera apenas as transcrições TXT sem sintetizar MP3.")
    parser.add_argument("--data", type=str, default="", help="Sobrescreve a data ISO da edição (ex.: 2026-11-19).")
    args, _ = parser.parse_known_args()

    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).strftime("%Y-%m-%d")

    edicao_data = carregar_dados_edicao()
    cultural_data = carregar_radar_cultural()
    data_edicao = (
        args.data.strip()
        or (edicao_data.get("radar_edicao_dia", {}) or {}).get("data")
        or (edicao_data.get("pauta", {}).get("atual", {}) or {}).get("periodo")
        or hoje
    )

    print("=" * 80)
    print(f"🎙️ MOTOR DE ÁUDIO JORNALÍSTICO LUCHM v3 (VOZ ÚNICA · +3%) — {data_edicao}")
    print("=" * 80)

    roteiro_limpo = construir_roteiro_narrado(edicao_data, cultural_data, data_edicao)
    total_palavras = len(roteiro_limpo.split())
    total_chars = len(roteiro_limpo)
    est_min = total_palavras / 150.0  # pt-BR-AntonioNeural em +3%
    blocos = chunking_por_paragrafos(roteiro_limpo)

    print(f"   • Parágrafos: {len(roteiro_limpo.split(chr(10) + chr(10)))}")
    print(f"   • Blocos de síntese (≤ {LIMITE_CHUNK_CHARS} chars): {len(blocos)}")
    print(f"   • Volume total: {total_palavras} palavras ({total_chars:,} caracteres)")
    print(f"   • Duração estimada (+3%): {est_min:.1f} minutos\n")

    transcricao_atual = os.path.join(AUDIO_DIR, "briefing_atual.txt")
    transcricao_dated = os.path.join(AUDIO_DIR, f"podcast_comutacao_28min_{data_edicao}.txt")

    cabecalho = (
        f"# Boletim Científico Narrado LUCHM (Stork Cast) — Edição de {formatar_data_extenso(data_edicao)}\n"
        f"# Voz oficial: {VOZ_PRINCIPAL} (rate={TAXA_PRINCIPAL}) | Chunking: {len(blocos)} blocos (≤ {LIMITE_CHUNK_CHARS} chars)\n"
        f"# Duração estimada: {est_min:.1f} minutos ({total_palavras} palavras)\n\n"
    )
    conteudo_com_cabecalho = cabecalho + roteiro_limpo + "\n"

    with open(transcricao_atual, "w", encoding="utf-8") as f:
        f.write(conteudo_com_cabecalho)
    with open(transcricao_dated, "w", encoding="utf-8") as f:
        f.write(conteudo_com_cabecalho)
    print(f"   ✅ Transcrição salva em {transcricao_atual} e {transcricao_dated}")

    downloads_dir = os.path.expanduser("~/Downloads")
    if os.path.isdir(downloads_dir):
        try:
            downloads_txt = os.path.join(downloads_dir, f"LUCHM_Podcast_Transcricao_{data_edicao}.txt")
            with open(downloads_txt, "w", encoding="utf-8") as f:
                f.write(roteiro_limpo + "\n")
            print(f"   ✅ Transcrição limpa sincronizada em Downloads: {downloads_txt}")
        except Exception as e:
            print(f"   ⚠️ Aviso ao salvar TXT em Downloads: {e}")

    if args.somente_texto:
        print("\n🏁 Modo --somente-texto concluído.")
        return

    master_mp3 = os.path.join(AUDIO_DIR, "briefing_atual.mp3")
    dated_mp3 = os.path.join(AUDIO_DIR, f"podcast_comutacao_28min_{data_edicao}.mp3")
    downloads_mp3 = os.path.expanduser(f"~/Downloads/LUCHM_Podcast_Comutacao_{data_edicao}.mp3")
    drive_dir = os.path.expanduser(
        "~/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast/episodes"
    )

    ok = await gerar_audio_jornalistico(roteiro_limpo, master_mp3)
    if not ok:
        print("❌ Falha ao gerar áudio MP3.")
        sys.exit(1)

    shutil.copyfile(master_mp3, dated_mp3)
    try:
        shutil.copyfile(master_mp3, downloads_mp3)
        print(f"   ✅ Áudio salvo em Downloads: {downloads_mp3}")
    except Exception as e:
        print(f"   ⚠️ Aviso ao salvar em Downloads: {e}")

    if os.path.exists(drive_dir):
        try:
            drive_out = os.path.join(drive_dir, f"stork-cast-{data_edicao}-profundo-28min.mp3")
            shutil.copyfile(master_mp3, drive_out)
            print(f"   ✅ Áudio sincronizado com Google Drive: {drive_out}")
        except Exception as e:
            print(f"   ⚠️ Aviso ao salvar no Drive: {e}")

    print("\n" + "=" * 80)
    print("🏁 ÁUDIO JORNALÍSTICO v3 CONCLUÍDO COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
