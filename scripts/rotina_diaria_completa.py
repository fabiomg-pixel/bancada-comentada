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
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_DIR, "scripts")
DATA_DIR = os.path.join(REPO_DIR, "data")
SECOND_BRAIN_DIR = "/Users/fabiogomes/second-brain"
DRIVE_PODCAST_DIR = "/Users/fabiogomes/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast"

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return res.returncode == 0, res.stdout.strip(), res.stderr.strip()

def executar():
    hoje = datetime.now().strftime("%Y-%m-%d")
    print("=" * 70)
    print(f"🚀 INICIANDO ROTINA DIÁRIA DO LUCHM — {hoje}")
    print("=" * 70)

    # ---------------------------------------------------------
    # PASSO 1: Sincronizar escolhas com o Second Brain (se local)
    # ---------------------------------------------------------
    sync_script = os.path.join(SCRIPTS_DIR, "sync_lab.py")
    if os.path.exists(sync_script) and os.path.exists(SECOND_BRAIN_DIR):
        print("\n[Passo 1/4] Sincronizando escolhas da Bancada com o Second Brain (Logseq)...")
        ok, out, err = run_cmd(f"python3 {sync_script}")
        if ok:
            print("   ✅ Second Brain sincronizado.")
        else:
            print(f"   ⚠️ Aviso na sincronização: {err}")
    else:
        print("\n[Passo 1/4] Ambiente em nuvem (ou sem second-brain local): pulando etapa de disco.")

    # ---------------------------------------------------------
    # PASSO 2: Varredura de Literatura (PubMed + bioRxiv)
    # ---------------------------------------------------------
    print("\n[Passo 2/4] Executando varredura da literatura (PubMed + bioRxiv)...")
    fetch_script = os.path.join(SCRIPTS_DIR, "fetch_literature.py")
    if os.path.exists(fetch_script):
        ok, out, err = run_cmd(f"python3 {fetch_script}", cwd=REPO_DIR)
        if ok:
            print(f"   ✅ Captura concluída.")
        else:
            print(f"   ⚠️ Aviso na captura: {err}")
    else:
        print(f"   ❌ Script não encontrado: {fetch_script}")

    # ---------------------------------------------------------
    # PASSO 3: Triagem Calibrada (26 temas do Notion + corte de ruído)
    # ---------------------------------------------------------
    print("\n[Passo 3/4] Aplicando triagem calibrada com pesos de vigilância do LUCHM...")
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
    # PASSO 4: Gerar Roteiro do Podcast (se Google Drive local)
    # ---------------------------------------------------------
    print("\n[Passo 4/4] Gerando entregáveis adicionais...")
    edicao_file = os.path.join(DATA_DIR, "edicao_atual.json")
    if os.path.exists(edicao_file) and os.path.exists(DRIVE_PODCAST_DIR):
        with open(edicao_file, "r", encoding="utf-8") as f:
            dados = json.load(f)
        artigos = list(dados.get("colecao_artigos", {}).values())
        altas = [a for a in artigos if a.get("importancia") == "alta"]
        if altas:
            roteiro_path = os.path.join(DRIVE_PODCAST_DIR, f"roteiro-{hoje}.txt")
            linhas_roteiro = [
                f"# Stork Cast — {hoje}",
                "A = Luciana | B = Reed\n",
                f"A: Olá Fábio, bom fim de tarde. Aqui estão os {len(altas)} destaques essenciais da bancada de hoje.",
            ]
            for i, a in enumerate(altas[:5]):
                tit = a.get("titulo")
                rev = a.get("revista")
                imp = a.get("implicacao")
                met = a.get("metodo")
                linhas_roteiro.append(f"B: Destaque {i+1}: {tit}, publicado na {rev}.")
                linhas_roteiro.append(f"A: Na nossa bancada, o ponto central é: {imp}")
                if met:
                    linhas_roteiro.append(f"B: E no método: {met}")
            linhas_roteiro.append("A: Esse foi o resumo de hoje. Boa volta para casa e até amanhã no laboratório!")
            
            with open(roteiro_path, "w", encoding="utf-8") as rf:
                rf.write("\n\n".join(linhas_roteiro))
            print(f"   ✅ Roteiro Stork Cast gerado em: {roteiro_path}")

    print("\n" + "=" * 70)
    print(f"🏁 ROTINA EXECUTADA COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    executar()
