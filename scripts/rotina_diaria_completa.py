#!/usr/bin/env python3
"""
rotina_diaria_completa.py — Pipeline diário autônomo do LUCHM
Executa de forma 100% autônoma no GitHub Actions ou no Mac local:
1. Sincroniza marcações (Bancada Comentada -> Second Brain / Logseq) se local
2. Varre a literatura (PubMed 7 blocos + bioRxiv)
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
    # PASSO 2: Varredura de Literatura Calibrada v6 (PubMed + bioRxiv)
    # ---------------------------------------------------------
    print("\n[Passo 2/5] Executando varredura da literatura calibrada v6...")
    fetch_script = os.path.join(SCRIPTS_DIR, "fetch_literature.py")
    if os.path.exists(fetch_script):
        ok, out, err = run_cmd(f"python3 {fetch_script}", cwd=REPO_DIR)
        if ok:
            print(f"   ✅ Captura v6 concluída.")
        else:
            print(f"   ⚠️ Aviso na captura: {err}")
    else:
        print(f"   ❌ Script não encontrado: {fetch_script}")

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
    # PASSO 4: Triagem Calibrada (26 temas do Notion + corte de ruído)
    # ---------------------------------------------------------
    print("\n[Passo 4/5] Aplicando triagem calibrada com ancoragem em programas LUCHM...")
    reclass_script = os.path.join(SCRIPTS_DIR, "reclassificar.py")
    if os.path.exists(reclass_script):
        ok, out, err = run_cmd(f"python3 {reclass_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Edição atualizada com sucesso.")
        else:
            print(f"   ⚠️ Erro na classificação: {err}")
    else:
        print(f"   ❌ Script não encontrado: {reclass_script}")

    # ---------------------------------------------------------
    # PASSO 5: Gerar Áudio Briefing / Podcast Diário (Edge-TTS)
    # ---------------------------------------------------------
    print("\n[Passo 5/5] Gerando síntese em áudio (Briefing Diário / Podcast)...")
    audio_script = os.path.join(SCRIPTS_DIR, "gerar_audio_briefing.py")
    if os.path.exists(audio_script):
        ok, out, err = run_cmd(f"python3 {audio_script}", cwd=REPO_DIR)
        if ok:
            print("   ✅ Áudio briefing sintetizado com sucesso.")
        else:
            print(f"   ⚠️ Aviso na geração de áudio: {err}")
    else:
        print(f"   ❌ Script não encontrado: {audio_script}")

    print("\n" + "=" * 70)
    print(f"🏁 ROTINA EXECUTADA COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    executar()
