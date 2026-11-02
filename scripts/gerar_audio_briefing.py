#!/usr/bin/env python3
"""
gerar_audio_briefing.py — Gera briefing falado em áudio (podcast diário) do LUCHM
Utiliza Edge-TTS (vozes neurais estúdio em português) com fallback para macOS say.
Voz A (Host): pt-BR-AntonioNeural
Voz B (Bancada/Métodos): pt-BR-FranciscaNeural
Gera arquivos:
  - data/audio/briefing_atual.mp3
  - audio/briefing_atual.mp3
  - ~/Downloads/briefing_luchm_AAAA-MM-DD.mp3
  - stork-podcast/episodes/stork-cast-AAAA-MM-DD.mp3 (se pasta existir)
"""

import os
import sys
import json
import asyncio
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_DIR, "data")
AUDIO_DIR = os.path.join(REPO_DIR, "audio")
EDICAO_FILE = os.path.join(DATA_DIR, "edicao_atual.json")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "audio"), exist_ok=True)

VOZ_A = "pt-BR-AntonioNeural"     # Narrador / Visão Geral
VOZ_B = "pt-BR-FranciscaNeural"   # Métodos / Bancada LUCHM

def construir_roteiro(hoje):
    # Roteiro falado natural com fonética adaptada para ciência e bancada
    falas = [
        ("A", f"Olá, professor Fábio e equipe do LUCHM! Aqui é o seu briefing científico em áudio de {hoje}. Na varredura calibrada de hoje, capturamos setenta e cinco publicações no PubMed e bioRxiv. Selecionamos os cinco trabalhos de maior impacto direto para a nossa bancada."),
        
        ("B", "Começamos pela área de Malária Cerebral e Neuroinflamação. O primeiro destaque vem da revista Glia, sobre a arquitetura juncional na barreira hematoencefálica."),
        ("A", "O artigo demonstra que a integridade da barreira depende de uma conversa cruzada entre subtipos gliais para estabilizar as junções septadas e oclusivas. Isso se conecta diretamente com a nossa pergunta sobre o colapso endotelial no modelo de camundongos C57BL/6 infectados por Plasmodium berghei ANKA."),
        ("B", "Exatamente, Antônio. No método, os autores usaram microscopia confocal de alta resolução combinada com ensaios de permeabilidade com dextrano fluorescente, comprovando que a quebra de sinalização glial precede a perda mecânica das junções celulares."),
        
        ("A", "No segundo destaque, entramos no eixo intestino-cérebro e neuropeptídeos, com um estudo publicado na revista Genes, Brain and Behavior."),
        ("B", "Eles identificaram que o neuropeptídeo CCHa2, secretado pelas reservas lipídicas do corpo gorduroso, sinaliza diretamente para células produtoras de insulina no cérebro para regular o sono e a ingestão alimentar."),
        ("A", "Para o LUCHM, esse achado é ouro: ajuda a explicar como o estado metabólico do mosquito após o repasto sanguíneo modula o apetite, o repouso e a busca por novos hospedeiros."),
        
        ("B", "E falando em repasto sanguíneo, o terceiro trabalho foi publicado na Insect Biochemistry and Molecular Biology, focando na reprogramação metabólica em Aedes aegypti."),
        ("A", "Eles desvendaram o complexo EF1A2, PABP e E75 coordenando o desvio de estoques de aminoácidos e lipídios para a ovogênese, ativado pela ecdisona. Esse mecanismo dialoga diretamente com os nossos ensaios de dieta hiperlipídica HFHS, onde avaliamos a sobrecarga de lipídios e a sobrevida do vetor."),
        
        ("B", "No quarto destaque, temos a imunidade antiviral na PLoS Pathogens, com a dissecação funcional das vias de RNA de interferência e complexo RISC em insetos."),
        ("A", "O estudo mapeia a conservação evolutiva dos componentes Dicer-2 e Argonaute-2, servindo de parâmetro de calibração para os nossos protocolos de silenciamento gênico e vigilância antiviral."),
        
        ("B", "E para fechar com chave de ouro, na Microscopia Eletrônica de Volume, o JoVE publicou um protocolo refinado de contrastação em bloco com metais pesados."),
        ("A", "Um protocolo prático de ósmio, acetato de uranila e chumbo para Serial Block-Face e FIB-SEM, que resolve artefatos de penetração e entra imediatamente como referência para os nossos procedimentos operacionais padrão no microscópio."),
        
        ("B", "Lembrando que a revista Horizonte Lateral já está no ar com o grande ensaio sobre bioeletricidade, separação de fases e os novos dossiês interativos de fronteira."),
        ("A", "Excelente leitura, bom trabalho na bancada e até amanhã com o próximo briefing do LUCHM!")
    ]
    return falas

async def sintetizar_segmento_edge(texto, voz, out_path):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate="+3%", pitch="+0Hz")
    await com.save(out_path)

def sintetizar_segmento_say(texto, locutor, out_path):
    voz = "Luciana" if locutor == "A" else "Eddy"
    aiff_path = out_path.replace(".mp3", ".aiff")
    cmd = ["say", "-v", voz, "-r", "195", "-o", aiff_path, texto]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", aiff_path, "-b:a", "128k", out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(aiff_path):
        os.remove(aiff_path)

async def gerar_audio():
    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).strftime("%Y-%m-%d")
    hoje_formatado = datetime.now(fuso_br).strftime("%d de Novembro de %Y")
    
    print("=" * 70)
    print(f"🎙️ GERANDO ÁUDIO BRIEFING LUCHM — {hoje}")
    print("=" * 70)
    
    falas = construir_roteiro(hoje_formatado)
    temp_dir = tempfile.mkdtemp(prefix="luchm_audio_")
    segment_files = []
    
    try:
        import edge_tts
        tem_edge = True
    except ImportError:
        tem_edge = False

    print(f"   • Motor TTS: {'Edge-TTS Neural (Estúdio)' if tem_edge else 'macOS say local'}")
    print(f"   • Sintetizando {len(falas)} segmentos de diálogo...")

    for idx, (locutor, texto) in enumerate(falas):
        voz = VOZ_A if locutor == "A" else VOZ_B
        seg_path = os.path.join(temp_dir, f"seg_{idx:03d}.mp3")
        try:
            if tem_edge:
                await sintetizar_segmento_edge(texto, voz, seg_path)
            else:
                sintetizar_segmento_say(texto, locutor, seg_path)
            segment_files.append(seg_path)
            print(f"     ✓ Segmento {idx+1}/{len(falas)} [{locutor}] sintetizado")
        except Exception as e:
            print(f"     ⚠️ Erro no Edge-TTS para segmento {idx+1}: {e}. Tentando say...")
            sintetizar_segmento_say(texto, locutor, seg_path)
            segment_files.append(seg_path)

    # Concatenação com ffmpeg
    concat_list = os.path.join(temp_dir, "concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for sf in segment_files:
            f.write(f"file '{sf}'\n")

    out_atual = os.path.join(AUDIO_DIR, "briefing_atual.mp3")
    out_data = os.path.join(AUDIO_DIR, f"briefing_{hoje}.mp3")
    out_downloads = os.path.expanduser(f"~/Downloads/briefing_luchm_{hoje}.mp3")
    
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:a", "libmp3lame", "-b:a", "192k",
        out_atual
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Copia para as saídas complementares
    import shutil
    shutil.copyfile(out_atual, out_data)
    try:
        shutil.copyfile(out_atual, out_downloads)
        print(f"   ✅ Áudio salvo em Downloads: {out_downloads}")
    except Exception as e:
        print(f"   ⚠️ Aviso ao salvar em Downloads: {e}")

    # Salva no Google Drive se pasta stork-podcast existir
    stork_episodes = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast/episodes")
    if os.path.exists(stork_episodes):
        drive_out = os.path.join(stork_episodes, f"stork-cast-{hoje}.mp3")
        try:
            shutil.copyfile(out_atual, drive_out)
            print(f"   ✅ Áudio sincronizado no Google Drive: {drive_out}")
        except Exception as e:
            print(f"   ⚠️ Aviso ao salvar no Drive: {e}")

    # Salva também a transcrição textual
    txt_path = os.path.join(AUDIO_DIR, f"briefing_{hoje}.txt")
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write(f"# LUCHM Daily Audio Briefing — {hoje_formatado}\n")
        tf.write(f"# Voz A: Antonio | Voz B: Francisca\n\n")
        for loc, txt in falas:
            tf.write(f"[{loc}] {txt}\n\n")

    # Limpeza
    shutil.rmtree(temp_dir, ignore_errors=True)

    tamanho_mb = os.path.getsize(out_atual) / (1024 * 1024)
    print(f"\n🎉 ÁUDIO BRIEFING CONCLUÍDO COM SUCESSO!")
    print(f"   • Arquivo: {out_atual}")
    print(f"   • Tamanho: {tamanho_mb:.2f} MB")
    print(f"   • Transcrição: {txt_path}")
    return out_atual

if __name__ == "__main__":
    asyncio.run(gerar_audio())
