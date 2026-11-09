#!/usr/bin/env python3
"""
rotina_diaria_completa.py — Pipeline diário autônomo do LUCHM
Executa de forma 100% autônoma no GitHub Actions ou no Mac local:
1. Sincroniza marcações (Bancada Comentada -> Second Brain / Logseq) se local
2. Importa o depósito do dia da revista do claude.ai (data/captura_v6/, escrito pela
   tarefa "Espelho da Bancada no GitHub"). Desde 09/11/2026 este repositório é espelho
   e não varre PubMed nem bioRxiv por conta própria (decisão do Fábio, D8).
3. Triagem calibrada com os 26 temas de vigilância do Notion + corte de ruído
4. Atualiza a revista Bancada Comentada (data/edicao_atual.json e index.html)
5. Gera roteiro do podcast Stork Cast se rodando no Mac
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_DIR, "scripts")
DATA_DIR = os.path.join(REPO_DIR, "data")

def get_second_brain_dir():
    candidates = [
        os.environ.get("SECOND_BRAIN_DIR"),
        os.path.expanduser("~/second-brain"),
        os.path.expanduser("~/Documents/second-brain"),
        "/Users/fabiomendoncagomes/second-brain",
        "/Users/fabiogomes/second-brain",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def get_podcast_dir():
    candidates = [
        os.environ.get("DRIVE_PODCAST_DIR"),
        os.path.expanduser("~/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast"),
        os.path.expanduser("~/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/My Drive/Laboratório/LUCHM/Claude Code/stork-podcast"),
        "/Users/fabiomendoncagomes/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast",
        "/Users/fabiogomes/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return res.returncode == 0, res.stdout.strip(), res.stderr.strip()

def executar():
    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).strftime("%Y-%m-%d")
    print("=" * 70)
    print(f"🚀 INICIANDO ROTINA DIÁRIA DO LUCHM — {hoje}")
    print("=" * 70)

    # ---------------------------------------------------------
    # PASSO 1: Sincronizar escolhas com o Second Brain (se local)
    # ---------------------------------------------------------
    sync_script = os.path.join(SCRIPTS_DIR, "sync_lab.py")
    second_brain_dir = get_second_brain_dir()
    if os.path.exists(sync_script) and second_brain_dir:
        print(f"\n[Passo 1/4] Sincronizando escolhas da Bancada com o Second Brain em {second_brain_dir}...")
        ok, out, err = run_cmd(f"python3 {sync_script}")
        if ok:
            print("   ✅ Second Brain sincronizado.")
        else:
            print(f"   ⚠️ Aviso na sincronização: {err}")
    else:
        print("\n[Passo 1/4] Ambiente em nuvem (ou sem second-brain local): pulando etapa de disco.")

    # ---------------------------------------------------------
    # PASSO 2: Importar o depósito da v6 (espelho, sem captura própria)
    # ---------------------------------------------------------
    print("\n[Passo 2/5] Importando o depósito do dia da revista do claude.ai (data/captura_v6/)...")
    import_script = os.path.join(SCRIPTS_DIR, "importar_v6.py")
    res = subprocess.run(["python3", import_script], cwd=REPO_DIR, capture_output=True, text=True)
    print("   " + (res.stdout.strip() or res.stderr.strip()).replace("\n", "\n   "))
    if res.returncode == 10:
        print("\n🛑 Nada novo da v6 desde a última edição: a edição e o podcast ficam como estão.")
        return
    if res.returncode != 0:
        print("\n❌ Falha ao importar o depósito da v6: a edição e o podcast ficam como estão.")
        sys.exit(1)

    # ---------------------------------------------------------
    # PASSO 3: Radar Cultural (Ensaio & Grandes Temas)
    # ---------------------------------------------------------
    print("\n[Passo 3/5] Atualizando dossiê do Radar Cultural...")
    cultural_script = os.path.join(SCRIPTS_DIR, "gerar_radar_cultural.py")
    if os.path.exists(cultural_script):
        ok, out, err = run_cmd(f"python3 {cultural_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Radar Cultural sincronizado.")
        else:
            print(f"   ⚠️ Aviso no Radar Cultural: {err}")

    # ---------------------------------------------------------
    # PASSO 4: Triagem Calibrada e Enriquecimento Profundo (Gemini 3.8 Flash)
    # ---------------------------------------------------------
    print("\n[Passo 4/5] Aplicando triagem calibrada e enriquecimento profundo com Gemini 3.8 Flash...")
    reclass_script = os.path.join(SCRIPTS_DIR, "reclassificar.py")
    if os.path.exists(reclass_script):
        ok, out, err = run_cmd(f"python3 {reclass_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Classificação básica concluída.")
        else:
            print(f"   ⚠️ Erro na classificação: {err}")
    else:
        print(f"   ❌ Script não encontrado: {reclass_script}")

    flash_script = os.path.join(SCRIPTS_DIR, "enriquecer_tudo_flash38.py")
    if os.path.exists(flash_script):
        print("   🧠 Executando síntese profunda dos 5 blocos com Gemini 3.8 Flash...")
        ok, out, err = run_cmd(f"python3 {flash_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Artigos enriquecidos densamente com Gemini 3.8 Flash e embutidos no index.html.")
        else:
            print(f"   ⚠️ Erro no enriquecimento Flash 3.8: {err}")
    else:
        print(f"   ❌ Script não encontrado: {flash_script}")

    # ---------------------------------------------------------
    # PASSO 5: Gerar Podcast Científico Profundo de Bancada (25-30 min)
    # ---------------------------------------------------------
    print("\n[Passo 5/5] Gerando podcast científico profundo de bancada (25-30 min)...")
    podcast_script = os.path.join(SCRIPTS_DIR, "gerar_podcast_28min.py")
    if not os.path.exists(podcast_script):
        podcast_script = os.path.join(SCRIPTS_DIR, "gerar_audio_briefing.py")
    if os.path.exists(podcast_script):
        ok, out, err = run_cmd(f"python3 {podcast_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Podcast de bancada (25-30 min) sintetizado com sucesso.")
        else:
            print(f"   ⚠️ Aviso na geração do podcast: {err}")
    else:
        print(f"   ❌ Script não encontrado: {podcast_script}")

    print("\n" + "=" * 70)
    print(f"🏁 ROTINA EXECUTADA COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    executar()
