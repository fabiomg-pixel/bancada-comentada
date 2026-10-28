#!/usr/bin/env python3
"""
sync_lab.py — Sincroniza marcações da Bancada Comentada (GitHub Pages)
com o acervo do laboratório e o Second Brain (Logseq).

Uso:
    python3 scripts/sync_lab.py [--file caminho/para/interacoes.json] [--no-push]
"""

import sys
import os
import json
import re
import subprocess
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERACOES_FILE = os.path.join(REPO_DIR, "data", "interacoes.json")
EDICAO_FILE = os.path.join(REPO_DIR, "data", "edicao_atual.json")
SECOND_BRAIN_DIR = "/Users/fabiogomes/second-brain"
PAGES_DIR = os.path.join(SECOND_BRAIN_DIR, "pages")

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return res.returncode == 0, res.stdout.strip(), res.stderr.strip()

def gerar_citekey(artigo):
    autores = artigo.get("autores") or "autor"
    primeiro_autor = autores.split(",")[0].split(";")[0].split(" ")[0].lower()
    primeiro_autor = re.sub(r"[^a-z0-9]", "", primeiro_autor)
    ano = str(artigo.get("ano") or datetime.now().year)
    titulo = artigo.get("titulo") or "paper"
    palavras = re.findall(r"[a-zA-Z]{3,}", titulo)
    palavra = palavras[0].lower() if palavras else "artigo"
    return f"{primeiro_autor}{ano}{palavra}"

def sincronizar(arquivo_custom=None, sem_push=False):
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO BANCADA COMENTADA -> LABORATÓRIO & SECOND BRAIN")
    print("=" * 60)

    # 1. Puxar dados remotos do repo bancada-comentada
    if not arquivo_custom:
        print("\n1. Atualizando repositório bancada-comentada via git pull...")
        ok, out, err = run_cmd("git pull origin main", cwd=REPO_DIR)
        if ok:
            print(f"   Git pull: {out or 'Já atualizado.'}")
        else:
            print(f"   Aviso ao atualizar git: {err}")

    caminho_interacoes = arquivo_custom or INTERACOES_FILE
    if not os.path.exists(caminho_interacoes):
        print(f"❌ Arquivo de interações não encontrado: {caminho_interacoes}")
        return

    with open(caminho_interacoes, "r", encoding="utf-8") as f:
        interacoes = json.load(f)

    # 2. Carregar artigos da edição
    artigos_map = {}
    if os.path.exists(EDICAO_FILE):
        with open(EDICAO_FILE, "r", encoding="utf-8") as f:
            dados_edicao = json.load(f)
            for a in dados_edicao.get("artigos", []):
                aid = str(a.get("_id") or a.get("id") or a.get("pmid") or "")
                if aid:
                    artigos_map[aid] = a

    # 3. Mapear itens catalogados e anotações
    catalogo_ids = set()
    for cat_user in interacoes.get("catalogo", []):
        for aid in (cat_user.get("itens") or {}).keys():
            catalogo_ids.add(str(aid))

    anotacoes_map = {} # aid -> list of notes
    for an_user in interacoes.get("anotacoes", []):
        uid = an_user.get("_id") or "membro"
        for aid, dados in (an_user.get("porArtigo") or {}).items():
            itens = dados.get("itens") or []
            if itens:
                anotacoes_map.setdefault(str(aid), []).extend([
                    {**it, "autor": uid} for it in itens
                ])

    sinais_map = {}
    for uid, dados in (interacoes.get("sinais") or {}).items():
        for aid, tipo in (dados.get("itens") or {}).items():
            sinais_map.setdefault(str(aid), []).append(f"{uid}: {tipo}")

    alvo_ids = catalogo_ids.union(set(anotacoes_map.keys()))
    print(f"\n2. Interações encontradas:")
    print(f"   - Artigos no Catálogo do Grupo: {len(catalogo_ids)}")
    print(f"   - Artigos com Anotações/Citações: {len(anotacoes_map)}")
    print(f"   - Total de Artigos a processar para o Second Brain: {len(alvo_ids)}")

    if not alvo_ids:
        print("\nℹ️ Nenhuma nova anotação ou artigo catalogado no momento.")
        print("   Marque artigos no leitor e clique em 'Sincronizar' para alimentar o sistema!")
        return

    # 4. Escrever páginas no Second Brain (Logseq)
    if not os.path.exists(PAGES_DIR):
        print(f"❌ Diretório do Second Brain não encontrado em {PAGES_DIR}")
        return

    notas_criadas = 0
    notas_atualizadas = 0

    print(f"\n3. Atualizando grafo do Second Brain em {SECOND_BRAIN_DIR}...")
    for aid in alvo_ids:
        art = artigos_map.get(aid, {
            "titulo": f"Artigo {aid}",
            "autores": "Autoria não informada",
            "ano": datetime.now().year,
            "revista": "Revista não informada",
            "doi": "",
            "pmid": aid if aid.isdigit() else ""
        })

        citekey = gerar_citekey(art)
        page_path = os.path.join(PAGES_DIR, f"@{citekey}.md")
        is_nova = not os.path.exists(page_path)

        # Montar conteúdo markdown compatível com Logseq
        tema = art.get("tema") or "Geral"
        titulo = art.get("titulo", "").strip()
        autores = art.get("autores", "").strip()
        ano = art.get("ano", "")
        revista = art.get("revista", "").strip()
        doi = art.get("doi", "").strip()
        pmid = art.get("pmid", "").strip()
        implicacao = art.get("implicacao", "").strip()
        resumo = art.get("resumo", "").strip()
        metodo = art.get("metodo", "").strip()

        md_lines = [
            "type:: literatura",
            f"citekey:: {citekey}",
            f"titulo:: {titulo}",
            f"autores:: {autores}",
            f"ano:: {ano}",
            f"revista:: {revista}",
            f"doi:: {doi}",
            f"pmid:: {pmid}",
            f"tema:: [[{tema.capitalize()}]]",
            "origem:: [[Bancada Comentada]]",
            f"catalogado:: {'true' if aid in catalogo_ids else 'false'}",
        ]
        if implicacao:
            md_lines.append(f"implicacao:: {implicacao}")

        md_lines.append("")
        if resumo:
            md_lines.append("- ### Resumo")
            md_lines.append(f"\t- {resumo}")

        if metodo:
            md_lines.append("- ### Método em Destaque")
            md_lines.append(f"\t- {metodo}")

        # Anotações da equipe
        art_anotacoes = anotacoes_map.get(aid, [])
        if art_anotacoes:
            md_lines.append("- ### Anotações da Bancada")
            for an in art_anotacoes:
                tipo = an.get("tipo", "nota").upper()
                trecho = an.get("trecho", "").strip()
                nota = an.get("nota", "").strip()
                autor = an.get("autor", "grupo")
                data_an = an.get("em", "")[:10]
                md_lines.append(f"\t- **[{tipo}]** [[{autor}]] em {data_an}:")
                if trecho:
                    md_lines.append(f"\t\t- > \"{trecho}\"")
                if nota:
                    md_lines.append(f"\t\t- {nota}")

        # Conceitos inferidos para backlinks no Logseq
        conceitos = []
        if tema: conceitos.append(tema.capitalize())
        if "aedes" in titulo.lower() or "aedes" in resumo.lower(): conceitos.append("Aedes aegypti")
        if "plasmodium" in titulo.lower() or "malaria" in titulo.lower(): conceitos.append("Plasmodium")
        if "cerebral" in titulo.lower(): conceitos.append("Malária Cerebral")
        if "imunometabolismo" in titulo.lower() or "metabolismo" in titulo.lower(): conceitos.append("Imunometabolismo")
        if "polifosfato" in titulo.lower(): conceitos.append("Polifosfato")

        if conceitos:
            md_lines.append("- ### Conceitos")
            for c in conceitos:
                md_lines.append(f"\t- [[{c}]]")

        with open(page_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")

        if is_nova:
            notas_criadas += 1
            print(f"   [+] Nova nota criada: @{citekey} ({titulo[:45]}...)")
        else:
            notas_atualizadas += 1
            print(f"   [*] Nota atualizada: @{citekey}")

    # Atualizar Índice Geral da Bancada Comentada no Logseq
    indice_path = os.path.join(PAGES_DIR, "Bancada Comentada.md")
    hoje = datetime.now().strftime("%Y-%m-%d")
    with open(indice_path, "a", encoding="utf-8") as f:
        f.write(f"\n- ## Sincronização em [[{hoje}]]\n")
        for aid in alvo_ids:
            art = artigos_map.get(aid, {})
            ck = gerar_citekey(art)
            tit = art.get("titulo", aid)
            f.write(f"\t- [[@{ck}]] — {tit}\n")

    print(f"\n4. Resumo Logseq: {notas_criadas} novas notas, {notas_atualizadas} atualizadas.")

    # 5. Git commit e push no Second Brain
    if not sem_push:
        print("\n5. Commitando e sincronizando no repositório second-brain...")
        run_cmd("git add pages/", cwd=SECOND_BRAIN_DIR)
        ok_commit, out_c, _ = run_cmd(
            f'git commit -m "Bancada Comentada: sincronização de {len(alvo_ids)} papers"',
            cwd=SECOND_BRAIN_DIR
        )
        if ok_commit:
            ok_push, out_p, err_p = run_cmd("git push origin main", cwd=SECOND_BRAIN_DIR)
            if ok_push:
                print("   ✅ Second Brain atualizado no GitHub com sucesso!")
            else:
                print(f"   Aviso no git push do second-brain: {err_p}")
        else:
            print("   (Sem novas alterações pendentes no git do second-brain)")

    print("\n" + "=" * 60)
    print("✅ SINCRONIZAÇÃO COMPLETA!")
    print("=" * 60)

if __name__ == "__main__":
    arq = None
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            arq = sys.argv[idx + 1]
    sincronizar(arquivo_custom=arq, sem_push="--no-push" in sys.argv)
