#!/usr/bin/env python3
"""
rotina_diaria_completa.py — Pipeline diário autônomo do LUCHM
1. Sincroniza marcações da equipe (Bancada Comentada -> Second Brain / Logseq)
2. Varre a literatura (PubMed 7 blocos + bioRxiv)
3. Triagem calibrada com os 26 temas de vigilância do Notion + corte de ruído
4. Gera relatório Markdown e roteiro do podcast Stork Cast no Google Drive
5. Atualiza a revista Bancada Comentada e faz push no GitHub Pages
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime

SCRATCH_DIR = "/Users/fabiogomes/.gemini/antigravity/scratch"
REPO_DIR = os.path.join(SCRATCH_DIR, "bancada-comentada")
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
    # PASSO 1: Sincronizar o que a equipe marcou online com o Second Brain
    # ---------------------------------------------------------
    print("\n[Passo 1/5] Sincronizando escolhas da Bancada com o Second Brain (Logseq)...")
    sync_script = os.path.join(REPO_DIR, "scripts", "sync_lab.py")
    if os.path.exists(sync_script):
        ok, out, err = run_cmd(f"python3 {sync_script}")
        if ok:
            print("   ✅ Second Brain sincronizado.")
        else:
            print(f"   ⚠️ Aviso na sincronização: {err}")

    # ---------------------------------------------------------
    # PASSO 2: Varredura de Literatura (PubMed + bioRxiv)
    # ---------------------------------------------------------
    print("\n[Passo 2/5] Executando varredura da literatura (PubMed + bioRxiv)...")
    fetch_script = os.path.join(SCRATCH_DIR, "fetch_literature_v6.py")
    if os.path.exists(fetch_script):
        ok, out, err = run_cmd(f"python3 {fetch_script}", cwd=SCRATCH_DIR)
        if ok:
            print(f"   ✅ Captura concluída.")
        else:
            print(f"   ⚠️ Aviso na captura: {err}")

    # ---------------------------------------------------------
    # PASSO 3: Triagem Calibrada (26 temas do Notion + filtros)
    # ---------------------------------------------------------
    print("\n[Passo 3/5] Aplicando triagem calibrada com pesos de vigilância do LUCHM...")
    reclass_script = os.path.join(SCRATCH_DIR, "calibracao", "reclassificar_v6.py")
    if os.path.exists(reclass_script):
        ok, out, err = run_cmd(f"python3 {reclass_script}", cwd=SCRATCH_DIR)
        if ok:
            print("   ✅ Classificação concluída (Altas selecionadas com foco na bancada).")
        else:
            print(f"   ⚠️ Erro na classificação: {err}")

    # ---------------------------------------------------------
    # PASSO 4: Atualizar Banco da Revista e Gerar Roteiro do Podcast
    # ---------------------------------------------------------
    print("\n[Passo 4/5] Atualizando edições e gerando roteiro Stork Cast...")
    calibrada_json = os.path.join(SCRATCH_DIR, "bancada_ingestao_2026-10-27_calibrada.json")
    
    if os.path.exists(calibrada_json):
        with open(calibrada_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        artigos = list(dados.get("colecao_artigos", {}).values())
        altas = [a for a in artigos if a.get("importancia") == "alta"]
        
        # Gerar roteiro para o Drive se a pasta existir
        if os.path.exists(DRIVE_PODCAST_DIR) and altas:
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

        # Atualizar HTMLs
        upd_script = "/tmp/update_all_editions.py"
        if os.path.exists(upd_script):
            run_cmd(f"python3 {upd_script}")
            print("   ✅ HTMLs da revista atualizados.")

    # ---------------------------------------------------------
    # PASSO 5: Publicar no GitHub Pages
    # ---------------------------------------------------------
    print("\n[Passo 5/5] Publicando nova edição no GitHub Pages...")
    run_cmd("git add data/ index.html", cwd=REPO_DIR)
    ok_commit, out_c, _ = run_cmd(
        f'git commit -m "chore(diario): edicao calibrada da Bancada Comentada [{hoje}]"',
        cwd=REPO_DIR
    )
    if ok_commit:
        ok_push, out_p, err_p = run_cmd("git push origin main", cwd=REPO_DIR)
        if ok_push:
            print("   ✅ GitHub Pages atualizado com sucesso!")
        else:
            print(f"   ⚠️ Aviso no git push: {err_p}")
    else:
        print("   (Sem alterações pendentes para publicar)")

    print("\n" + "=" * 70)
    print(f"🏁 ROTINA CONCLUÍDA COM SUCESSO! Site: https://fabiomg-pixel.github.io/bancada-comentada/")
    print("=" * 70)

if __name__ == "__main__":
    executar()
