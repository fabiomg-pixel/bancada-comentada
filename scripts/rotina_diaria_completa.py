#!/usr/bin/env python3
"""
rotina_diaria_completa.py — Pipeline diário autônomo do LUCHM (Modo Espelho v2)

Fluxo otimizado:
1. Sincroniza marcações (Bancada Comentada -> Second Brain / Logseq / Obsidian) se local
2. Importa a janela rolante de 14 dias de data/captura_v6/ (com cache de abstracts PubMed/bioRxiv)
3. Atualiza o dossiê mensal Horizonte Lateral (data/radar_cultural.json)
4. Executa triagem híbrida (v6 + High-Impact + 7 programas LUCHM + Vault) via reclassificar.py
5. Enriquece artigos prioritários novos (se GEMINI_API_KEY estiver ativa) e atualiza conexões transversais
6. Sintetiza o boletim narrado contínuo (pt-BR-AntonioNeural +3%, cache em /tmp, backup no Drive e retenção enxuta de MP3)
"""

import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_DIR, "scripts")


def get_second_brain_dir():
    candidates = [
        os.environ.get("SECOND_BRAIN_DIR"),
        os.path.expanduser("~/second-brain"),
        os.path.expanduser("~/Documents/second-brain"),
        "/Users/fabiogomes/second-brain",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def run_step(args_list, cwd=REPO_DIR):
    res = subprocess.run(args_list, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def executar():
    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).strftime("%Y-%m-%d")
    print("=" * 70)
    print(f"🚀 INICIANDO ROTINA DIÁRIA OTIMIZADA DO LUCHM — {hoje}")
    print("=" * 70)

    # PASSO 1: Second Brain & Obsidian
    sync_script = os.path.join(SCRIPTS_DIR, "sync_lab.py")
    sb_dir = get_second_brain_dir()
    if os.path.exists(sync_script) and sb_dir:
        print(f"\n[Passo 1/5] Sincronizando marcações com Second Brain ({sb_dir})...")
        code, _, err = run_step([sys.executable, sync_script])
        if code == 0:
            print("   ✅ Second Brain & Obsidian sincronizados.")
        else:
            print(f"   ⚠️ Aviso na sincronização: {err}")
    else:
        print("\n[Passo 1/5] Ambiente sem Second Brain local: pulando etapa de disco.")

    # PASSO 2: Importar janela rolante de 14 dias da captura v6
    print("\n[Passo 2/5] Importando depósitos da revista do claude.ai (data/captura_v6/, janela 14d)...")
    import_script = os.path.join(SCRIPTS_DIR, "importar_v6.py")
    code, out, err = run_step([sys.executable, import_script])
    print("   " + (out or err).replace("\n", "\n   "))
    if code == 10:
        print("\n🛑 Nada novo da v6 desde a última edição: a revista e o podcast permanecem atuais.")
        return
    if code != 0:
        print("\n❌ Falha ao importar o depósito da v6.")
        sys.exit(1)

    # PASSO 3: Horizonte Lateral
    print("\n[Passo 3/5] Atualizando dossiê Horizonte Lateral...")
    cultural_script = os.path.join(SCRIPTS_DIR, "gerar_radar_cultural.py")
    if os.path.exists(cultural_script):
        code, _, err = run_step([sys.executable, cultural_script])
        if code == 0:
            print("   ✅ Horizonte Lateral sincronizado.")
        else:
            print(f"   ⚠️ Aviso no Horizonte Lateral: {err}")

    # PASSO 4: Triagem Híbrida + Enriquecimento Analítico em 5 Blocos
    print("\n[Passo 4/5] Executando triagem híbrida (v6 + High-Impact + LUCHM) e enriquecimento em 5 blocos...")
    reclass_script = os.path.join(SCRIPTS_DIR, "reclassificar.py")
    code, out, err = run_step([sys.executable, reclass_script])
    if code == 0:
        print(f"   {out}")
    else:
        print(f"   ❌ Erro na classificação: {err}")
        sys.exit(1)

    flash_script = os.path.join(SCRIPTS_DIR, "enriquecer_tudo_flash38.py")
    if os.path.exists(flash_script):
        code, out, err = run_step([sys.executable, flash_script])
        if out:
            print("   " + out.replace("\n", "\n   "))
        if code != 0 and err:
            print(f"   ⚠️ Aviso no enriquecimento: {err}")

    # PASSO 5: Síntese Neural Contínua + Backup Drive + Retenção MP3
    print("\n[Passo 5/5] Sintetizando boletim narrado contínuo (25-28 min)...")
    podcast_script = os.path.join(SCRIPTS_DIR, "gerar_podcast_28min.py")
    code, out, err = run_step([sys.executable, podcast_script])
    if code == 0:
        print("   ✅ Boletim narrado sintetizado e sincronizado com sucesso.")
    else:
        print(f"   ⚠️ Aviso na geração de áudio: {err}")

    print("\n" + "=" * 70)
    print("🏁 ROTINA DIÁRIA CONCLUÍDA COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    executar()
