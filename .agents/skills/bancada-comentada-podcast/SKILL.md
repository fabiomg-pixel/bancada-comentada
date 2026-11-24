---
name: bancada-comentada-podcast
description: "Rotina operacional, regras inegociáveis e governança editorial da Bancada Comentada e do Boletim Narrado de 25-28 min (Stork Cast) do LUCHM/IBCCF/UFRJ para o Prof. Fábio Gomes: triagem híbrida v6 + High-Impact em janela rolante de 14 dias, enriquecimento denso em 5 blocos 100% em português, síntese neural contínua em voz única (pt-BR-AntonioNeural +3%) e exportação para Eleven Reader e Google Drive."
---

# Bancada Comentada & Boletim Científico Narrado LUCHM (Stork Cast)

Esta skill define as diretrizes estritas, a arquitetura técnica, os padrões editoriais e a rotina autônoma de execução da **Bancada Comentada** e do **Boletim Científico Diário de Bancada & Viagem de Carro** do Laboratório de Ultraestrutura Celular Hertha Meyer (**LUCHM/IBCCF/UFRJ**), sob liderança do **Prof. Fábio Gomes**.

---

## 1. Princípios Inegociáveis (Non-Negotiables)

Estas regras têm precedência absoluta em qualquer geração, edição ou manutenção do sistema:

1. **Curadoria em Português de Alto Rigor**:
   - Todo o enriquecimento analítico dos artigos prioritários deve ser redigido com densidade factual e rigor experimental (via agente local ou modelo **Google Gemini Flash** mais avançado disponível). É proibido o uso de textos truncados, telegráficos ou resumos genéricos.
   - Todo cartão da interface (`a.resumo`, `a.metodo`, `a.implicacao`, `a.resumo_blocos`) deve estar **100% em português**, mantendo o abstract integral em inglês em `a.resumo_original` para consulta na aba *"📄 Resumo Original (PubMed)"*.

2. **Densidade Textual & Rigor de Bancada (Anti-Hipersimplificação)**:
   - Cada bloco analítico dos artigos essenciais deve ter 3 a 5 frases completas contendo os dados empíricos reais reportados no estudo: modelos animais e de insetos (cepas murinas $PbA$/C57BL/6J, linhagens de *Aedes aegypti*, *Anopheles*, *Drosophila*, *Spodoptera*), concentrações, tempos cinéticos, alvos moleculares, técnicas (FIB-SEM, cryo-EM, metabolômica, RNAi) e controles experimentais explícitos — sem jamais inventar técnicas ausentes do abstract.

3. **Estrutura Canônica em 5 Blocos por Artigo (`data/cache_flash38_artigos.json`)**:
   - Chaves canônicas obrigatórias no cache: `programa_luchm`, `racional`, `metodo_bancada`, `resultados`, `implicacao_luchm`, `faisca_lateral`.
   - Exibição no leitor:
     - `1. 🎯 Racional & Pergunta Biológica`
     - `2. 🔬 Metodologia Experimental & Modelos`
     - `3. 📊 Principais Achados & Mecanismos Revelados`
     - `4. 💡 Implicação Direta para a Bancada LUCHM`
     - `5. ⚡ Faísca Lateral & Hipótese de Trabalho`

4. **Espelho sem Captura Própria + Triagem Híbrida em Janela de 14 Dias**:
   - A revista oficial é a do claude.ai, alimentada pela rotina *Resumo da Literatura Científica v6*. Este repositório é o espelho: a única entrada de literatura é `data/captura_v6/AAAA-MM-DD.json` (depositada às ~18h45 BRT) e lida por `scripts/importar_v6.py` em **janela rolante de 14 dias** (`DIAS_CIRCULACAO = 14`), com cache incremental de abstracts originais do PubMed/bioRxiv.
   - É proibido reativar os scripts arquivados em `scripts/legacy/`.
   - `scripts/reclassificar.py` funde os metadados curados da `v6` (`importancia`, `score`, `resumo`, `metodo`, `implicacao`) com bônus explícito para periódicos `HIGH_IMPACT` (*Nature*, *Science*, *Cell*, *Current Biology*, *Science Advances*, *PNAS*, *eLife*, *Nature Communications*, *PLoS Pathogens*) e ancoragem aos 7 programas do LUCHM, migrando automaticamente artigos `alta` ou interagidos após 14 dias para `estagio: "vault"`.

5. **Sincronismo Rigoroso & Antirrepetição Entre Episódios**:
   - Nunca atualizar o screening diário sem atualizar simultaneamente `pauta.atual.conexoes_transversais` (pós-enriquecimento) e o roteiro/áudio do podcast.
   - `gerar_podcast_28min.py` verifica as transcrições anteriores (`audio/podcast_comutacao_28min_*.txt`) para não repetir artigos já narrados e resgata automaticamente artigos `alta` inéditos das últimas 72h caso um dia anterior não tenha tido episódio publicado.

6. **Áudio Neural Contínuo em Voz Única + Eleven Reader**:
   - Locução contínua em voz única jornalística (`pt-BR-AntonioNeural`, `--rate=+3%` via `edge-tts`), sem cortes de alternância de interlocutores, fatiada em blocos de até 3.500 caracteres em quebras duplas de parágrafo (`\n\n`) e unida por concatenação binária direta.
   - A transcrição limpa é disponibilizada simultaneamente para cópia em 1 clique no **Eleven Reader**, leitura via **Web Speech API** nativa do navegador e download em `~/Downloads`.

7. **Duração Calibrada para a Viagem de Carro (25 a 28 Minutos)**:
   - O roteiro contínuo é calibrado por orçamento adaptativo entre **3.400 e 3.880 palavras** (~25 a 28 minutos em `+3%`).

8. **Isolamento de Cache Temporário e Retenção Enxuta no Git**:
   - Os fragmentos temporários de síntese ficam estritamente isolados em `/tmp/luchm_podcast_{data_edicao}/` com hash SHA-256 por bloco.
   - Todos os episódios MP3 históricos são preservados no Google Drive (`stork-podcast/episodes/`), mantendo em `audio/` no Git apenas `briefing_atual.mp3` + os **3 últimos** MP3 datados (e **100% das transcrições `.txt`**), evitando que o repositório ultrapasse o limite do GitHub Pages.

9. **Arquitetura Enxuta e Responsiva em `index.html`**:
   - `index.html` carrega `data/edicao_atual.json` assincronamente via `fetch()` em HTTP/HTTPS e usa `data/edicao_embedded.js` (ignorado no Git) como fallback automático em `file://`.
   - Na aba **Pauta**, mantém-se estritamente a arquitetura em faixas de largura total (`.wrap`): `.pauta-topo` → `.audio-sintese-dupla` (Áudio/Eleven Reader à esquerda + grade 2×2 `.sintese-eixos-grid` à direita) → listas em duas colunas `.fichas.fichas-duas-colunas`.

---

## 2. Os 7 Programas de Pesquisa do LUCHM (IBCCF/UFRJ)

1. **Malária Cerebral & Neuroinflamação**: Modelo murino C57BL/6J infectado com *Plasmodium berghei* ANKA ($PbA$); barreira hematoencefálica (claudina-5, occludina, ZO-1), astrócitos, micróglia, tromboinflamação microvascular, ferroptose endotelial, hemo livre e MIF/CD74.
2. **Repasto Sanguíneo HFHS & Metabolismo do Vetor**: *Aedes aegypti* e *Anopheles*; alimentação com sangue de camundongos obesos (dieta HFHS), peroxidação lipídica por hemo, ROS intestinal, eixo intestino-cérebro/neuropeptídeos (leucocinina/TrpA1), sono pós-prandial, gotas lipídicas e ovogênese.
3. **Imunidade de Vetores & RNAi**: Competência vetorial para Dengue, Zika, Chikungunya, Oropouche e WNV; vias de siRNA (Dicer-2/AGO2); imunidade antiviral e microbioma intestinal.
4. **Polifosfato Inorgânico & Acidocalcisomas**: Bioenergética e homeostase de cálcio/fósforo/poliânions em protozoários (*Trypanosoma cruzi*, *Plasmodium*) e insetos; exopolifosfatases e polifosfato quinases.
5. **Microscopia Eletrônica de Volume & Bioimagem**: Reconstrução 3D por FIB-SEM e SBF-SEM no CENABIO/UFRJ; contactoma de organelas (MCS); protocolo OTO e segmentação 3D.
6. **Biologia Celular de *Plasmodium* & Bloqueio de Transmissão**: Oocinetos, oocistos, esporozoítos e estágio hepático; fatores ApiAP2; invasão de glândula salivar (Saglin/SGS) e antígenos de bloqueio.
7. **Controle de Pragas & Bioinseticidas**: *Anticarsia gemmatalis* e *Spodoptera frugiperda*; toxinas Cry/Vip3 de *Bacillus thuringiensis*; receptores ABCC2/APN/ALP, matriz peritrófica e simbiontes (*Enterococcus mundtii*).

---

## 3. Fluxo Operacional Diário

```bash
cd /Users/fabiogomes/.gemini/antigravity/scratch/bancada-comentada

# 1. Atualizar capturas remotas
git pull --ff-only origin main

# 2. Importar janela rolante de 14 dias (só baixa abstracts inéditos)
python3 scripts/importar_v6.py

# 3. Atualizar Horizonte Lateral e classificar edição
python3 scripts/gerar_radar_cultural.py
python3 scripts/reclassificar.py

# 4. Após gravar curadorias PT novas em data/cache_flash38_artigos.json, reclassificar e gerar áudio
python3 scripts/reclassificar.py
python3 scripts/gerar_podcast_28min.py

# 5. Publicar no GitHub Pages (git status limpo e enxuto)
git add -A data/ index.html audio/
git commit -m "chore(neon): curadoria PT e audio continuo da edicao AAAA-MM-DD [skip ci]"
git push origin main
```
