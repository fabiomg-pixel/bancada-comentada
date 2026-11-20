---
name: bancada-comentada-podcast
description: "Rotina operacional, regras inegociáveis e governança editorial da Bancada Comentada e do Podcast Científico de 25-30 min (Stork Cast) do LUCHM/IBCCF/UFRJ para o Prof. Fábio Gomes: screening v6, enriquecimento denso Gemini 3.8 Flash em 5 blocos, síntese de áudio neural dinâmico para comutação e exportação para Eleven Reader."
---

# Bancada Comentada & Podcast Científico LUCHM (Stork Cast)

Esta skill define as diretrizes estritas, a arquitetura técnica, os padrões editoriais e a rotina autônoma de execução da **Bancada Comentada** e do **Podcast Científico Diário de Bancada & Viagem de Carro** do Laboratório de Ultraestrutura Celular Hertha Meyer (**LUCHM/IBCCF/UFRJ**), sob liderança do **Prof. Fábio Gomes**.

---

## 1. Princípios Inegociáveis (Non-Negotiables)

Estas regras têm precedência absoluta em qualquer geração, edição ou manutenção do sistema:

1. **Modelo de Linguagem Obrigatório**:
   - Todo o enriquecimento analítico dos artigos deve ser processado utilizando **Google Gemini 3.8 Flash** (ou o modelo Flash mais avançado disponível no ecossistema). É terminantemente proibido o uso de modelos depreciados, condensados ou simplificados (e.g. Gemini 2.5 Flash Lite ou equivalentes truncados).

2. **Densidade Textual & Rigor de Bancada (Anti-Hipersimplificação)**:
   - Proibido qualquer texto telegráfico, genérico ou superficial de duas frases.
   - Cada bloco de análise deve conter dados empíricos rigorosos: modelos animais e de insetos (cepas murinas $PbA$/C57BL/6J, linhagens de *Aedes aegypti*, *Anopheles*, *Spodoptera*), dosagens de fármacos, tempos cinéticos de ensaio, alvos moleculares, ensaios espectrofotométricos/fluorimétricos, técnicas de microscopia (FIB-SEM, confocal, TEM) e controles experimentais explícitos.

3. **Estrutura Canônica em 5 Blocos por Artigo**:
   - `1. 🎯 Racional & Pergunta Biológica`: O gargalo conceitual, o paradoxo ou o modelo prévio que o estudo desafia.
   - `2. 🔬 Metodologia Experimental & Modelos`: Os ensaios analíticos detalhados, traçadores, cepas e controles.
   - `3. 📊 Principais Achados & Mecanismos Revelados`: Os resultados fenotípicos quantitativos e as vias identificadas.
   - `4. 💡 Implicação Direta para a Bancada LUCHM`: Conexão direta e específica com os 7 programas de pesquisa do laboratório.
   - `5. ⚡ Faísca Lateral & Hipótese de Trabalho`: Hipótese provocativa e testável na bancada ou no biotério.

4. **Espelho sem Captura Própria (desde 09/11/2026, decisão do Fábio)**:
   - A revista oficial é a do claude.ai, alimentada pela rotina *Resumo da Literatura Científica v6*. Este repositório é o espelho: a única entrada de literatura é `data/captura_v6/AAAA-MM-DD.json`, gravado pela tarefa *Espelho da Bancada no GitHub*, e lido por `scripts/importar_v6.py`.
   - É proibido reativar `scripts/fetch_literature.py`, `fetch_literature_v6.py` ou qualquer outra varredura de PubMed, bioRxiv ou Stork aqui. A regra existe para que a mesma literatura não seja capturada duas vezes.
   - O enriquecimento em 5 blocos e o podcast continuam sendo deste repositório, sobre os artigos que a v6 depositou.

5. **Sincronismo Rigoroso & Fidelidade Factual (Anti-Alucinação)**:
   - Nunca atualizar o screening diário sem atualizar simultaneamente as sínteses transversais (`pauta.atual.conexoes_transversais`) e a transcrição do podcast.
   - O episódio DEVE cobrir apenas artigos reais presentes em `data/edicao_atual.json` e o dossiê vigente em `data/radar_cultural.json`, excluindo ruídos fora de escopo (e.g., revisões médicas não relacionadas) e vedando o uso de blocos metodológicos pré-fabricados (`Drosophila`, `32P-ortofosfato`, `PacBio`) aplicados por casamento frouxo de palavras-chave.
   - Nunca injetar frases cruas em inglês de abstracts no diálogo em português (`eh_texto_ingles` atua como barreira automática). Revistas e PMIDs citados devem corresponder estritamente ao registro da coleção.

6. **Eleven Reader como Fluxo Principal de Áudio Neural**:
   - Devido a cortes e transições abruptas de cadência entre interlocutores no `edge-tts` local, o **Eleven Reader** é o canal oficial de síntese de alta fidelidade vocal.
   - A transcrição gerada por `scripts/gerar_podcast_28min.py` (`--somente-texto` suportado para atualização instantânea sem síntese MP3) deve ser limpa, no formato estrito de diálogo (`Antônio:` e `Francisca:` separados por linha em branco), com botão primário no topo da pauta para copiar para a área de transferência (com fallback automático por `execCommand`/`textarea` em ambientes restritos).
   - O player local (`Edge-TTS` / MP3) permanece disponível exclusivamente como fallback secundário.

7. **Duração do Podcast Calibrada para a Viagem de Carro (25 a 28 Minutos)**:
   - O diálogo deve conter entre **3.500 e 3.850 palavras** (~45 a 50 intervenções balanceadas entre Antônio e Francisca).
   - Na cadência neural (~140 palavras/minuto), a duração final situa-se estritamente entre **25 e 28 minutos**, correspondendo ao trajeto de comutação do Prof. Fábio Gomes.

8. **Dossiê de Conexões Transversais Adjacente ao Áudio (`.audio-sintese-dupla`)**:
   - As análises mecanísticas e conexões entre artigos formuladas no podcast NÃO podem ficar presas apenas ao áudio.
   - A interface web DEVE renderizar `.audio-sintese-dupla` em **largura total da `.wrap`** (`max-width: 1280px`), colocando o cartão de Áudio/Eleven Reader à esquerda e `.sintese-transversal-box` à direita em grade `2×2` (`.sintese-eixos-grid`).
   - Cada eixo vem dinamicamente de `pauta.atual.conexoes_transversais` em `data/edicao_atual.json`, exibindo evidência, aplicação `Na nossa bancada` e chips clicáveis (`artigos_ref` abrindo `abrirLeitor(id)` e selo `horizonte_lateral` abrindo a aba `fronteira`).

9. **Layout em Duas Colunas em Largura Total para 'O Que Ler Antes da Reunião'**:
   - É proibido enclausurar `.audio-sintese-dupla` ou as listas de artigos dentro da coluna esquerda de uma grade de duas colunas junto à barra lateral `.lado` (o que gera um grande vazio vertical à direita abaixo da `.lado`).
   - `blocoPauta()` deve estruturar a aba em faixas horizontais independentes (`[cabeca, topo, faixaAudioSintese, secDestaques, secOutros]`): apenas `.pauta-topo` coloca o panorama ao lado de `.lado`, enquanto `.audio-sintese-dupla`, `o que ler antes da reunião` e `mais trabalhos em circulação` ocupam a largura total da `.wrap` em `.fichas.fichas-duas-colunas` (`grid-template-columns: repeat(2, minmax(0, 1fr))` acima de `860px`, cartões esticados em altura igual).

10. **Isolamento de Cache de Áudio**:
    - O diretório temporário de síntese de voz é particionado por data da edição (`/tmp/luchm_podcast_{data_edicao}`), prevenindo que resíduos de cache de dias anteriores impeçam novas sínteses.

---

## 2. Os 7 Programas de Pesquisa do LUCHM (IBCCF/UFRJ)

Todo artigo classificado ou discutido deve ancorar-se a um dos programas oficiais do laboratório:

1. **Malária Cerebral & Neuroinflamação**:
   - Modelo murino C57BL/6J infectado com *Plasmodium berghei* ANKA ($PbA$).
   - Permeabilidade da barreira hematoencefálica (BHE), junções oclusivas (claudina-5, occludina, ZO-1), pés vasculares de astrócitos (GFAP), micróglia (Iba-1), ferroptose endotelial, hemo livre e via protetora de MIF/CD74.
2. **Repasto Sanguíneo HFHS & Metabolismo do Vetor**:
   - Fêmeas de *Aedes aegypti* e *Anopheles aquasalis*.
   - Alimentação com sangue de camundongos obesos em dieta hiperlipídica/hiperglicêmica (HFHS); peroxidação lipídica mediada por hemo; estresse oxidativo intestinal; dinâmica de gotas lipídicas e ovogênese.
3. **Imunidade de Vetores & RNAi**:
   - Competência vetorial para Dengue, Zika, Chikungunya e Oropouche.
   - Vias de siRNA com Dicer-2 e Argonaute-2 (AGO2); imunidade antiviral; priming imune transgeracional.
4. **Polifosfato Inorgânico & Acidocalcisomas**:
   - Homeostase de bioenergética e armazenamento de cálcio/fósforo em protozoários (*Trypanosoma cruzi*, *Plasmodium*) e insetos; exopolifosfatases e polifosfato quinases; acidocalcisomos e regulação de pH.
5. **Microscopia Eletrônica de Volume & Bioimagem**:
   - Reconstrução 3D por FIB-SEM e SBF-SEM no CENABIO/UFRJ; sítios de contato de organelas (MCS); contrastação em bloco com metais pesados (protocolo OTO: ósmio-tiocarboidrazida-ósmio, acetato de uranila e chumbo de Walton a quente).
6. **Biologia Celular de *Plasmodium* & Bloqueio de Transmissão**:
   - Ciclo exoeritrocítico e esporozoítos; transição intestino-glândula salivar; antígenos de bloqueio (Pfs25, CSP).
7. **Controle de Pragas & Bioinseticidas**:
   - *Anticarsia gemmatalis* e *Spodoptera frugiperda*; toxinas Cry de *Bacillus thuringiensis*; receptores ABCC2; integridade da membrana peritrófica e modulação por bactérias simbiontes (*Enterococcus mundtii*).

---

## 3. O Módulo "Horizonte Lateral — Revista de Fronteiras & Ponto Cego"

Mensalmente, a revista integra a aba e dossiê **Horizonte Lateral** governada pelo teste de não-obviedade:
* **Regra de Ouro**: Nunca selecionar autores ou temas que trabalhem diretamente com culicídeos clássicos ou malária direta (evitar o que já é óbvio). Buscar disciplinas adjacentes (nanotribologia, bioeletricidade tecidual, física da matéria condensada, biologia celular de sistemas) que tragam princípios mecanicistas inovadores.
* **Composição do Dossiê**:
  1. *1 Grande Ensaio de Fundo & Ponto Cego* (história, 3 papers marco, ancoragem no LUCHM e 3 pontos de aprofundamento).
  2. *2 Pesquisadores de Referência Lateral* (trajetória, por que não é óbvio, 2 papers marco e cruzamento prático).
  3. *2 Temas em Expansão Lateral* (mecanismo físico, 2 papers marco e pontos de teste).
  4. *2 Técnicas Emergentes de Bancada* (resolução, limitações e viabilidade de implementação no CENABIO/LUCHM).

---

## 4. Arquitetura do Áudio Neural Jornalístico (Voz Única — Audio-First)

### Voz, Ritmo e Chunking Sem Cortes
* **Voz Oficial (Nível 1):** `pt-BR-AntonioNeural` via `edge-tts` (Python), com timbre sóbrio de âncora de rádio jornalismo e velocidade **`--rate=+3%`** (elimina o arrastado de TTS sem distorcer o tom).
* **Sem alternância picotada de personagens:** locução única contínua elimina os cortes e reinícios de prosódia entre turnos.
* **Chunking inteligente (≤ 3.500 caracteres):** o roteiro integral é fatiado estritamente em quebras duplas de parágrafo (`\n\n`) em ~6 a 8 blocos contínuos, unidos por **concatenação binária direta** (`fout.write(fin.read())`) sem estalos e sem inserção de silêncios artificiais.
* **Resiliência em 3 Camadas:**
  1. **Nível 1 (Principal):** `edge-tts` com `pt-BR-AntonioNeural` (`+3%`).
  2. **Nível 2 (Fallback Local Offline):** `say -v Luciana` (macOS) convertido para MP3 mono via `ffmpeg`.
  3. **Nível 3 (Navegador):** botão **"🔊 Ouvir com voz do navegador"** (`window.speechSynthesis`, `lang: pt-BR`, `rate: 1.03`) em `index.html`, além do botão **"📋 Copiar Transcrição (Eleven Reader)"**.

### Diretriz de Roteiro Audio-First
1. **Abertura Direta (< 30 segundos):** data expandida por extenso (*"Edição de 19 de novembro de 2026"* — nunca `"19/11"`), contagem de artigos triados/prioritários e entrada imediata no primeiro artigo (*"Vamos direto ao primeiro artigo."*).
2. **Cadência por Matéria:** editoria, periódico/PMID e título encerrados com **ponto final** para forçar pausas naturais de respiração, seguidos por 3 parágrafos contínuos (contexto/racional → método de bancada → achados) e arremate explícito **"Por que importa na bancada: ..."** (+ próximo passo no LUCHM).
3. **Vinhetas de Transição Faladas:** anúncio claro nas viradas de bloco (Plasmodium → Vetores & Arboviroses → Barreira Endotelial/Métodos → Horizonte Lateral → 3 Diretrizes Finais).

### Formato de Saída e Distribuição
* `audio/briefing_atual.txt` e `audio/podcast_comutacao_28min_{data_edicao}.txt`: Transcrição limpa em parágrafos narrados (sem rótulos de diálogo), pronta para Web Speech API e Eleven Reader.
* `~/Downloads/LUCHM_Podcast_Transcricao_{data_edicao}.txt`: Cópia sem cabeçalhos `#` pronta para importar diretamente no Eleven Reader.
* `audio/briefing_atual.mp3` e `audio/podcast_comutacao_28min_{data_edicao}.mp3`: Master MP3 contínuo gerado por concatenação binária direta dos blocos `edge-tts`.
* `~/Downloads/LUCHM_Podcast_Comutacao_{data_edicao}.mp3` e Google Drive (`stork-podcast/episodes/stork-cast-{data_edicao}-profundo-28min.mp3`): Sincronização automática.

---

## 5. Fluxo Operacional de Execução Diária (Modo Espelho)

A rotina é disparada autonomamente via GitHub Actions (`rotina_diaria.yml`, ao receber `data/captura_v6/**` ou via `workflow_dispatch`) ou localmente:

```bash
cd /Users/fabiogomes/.gemini/antigravity/scratch/bancada-comentada

# Executar pipeline completo no modo espelho (sync_lab -> importar_v6 -> radar_cultural -> reclassificar -> flash 3.8)
python3 scripts/rotina_diaria_completa.py
```

### Se for necessário rodar etapas de forma isolada:
```bash
# 1. Importar captura depositada pelo espelho v6 em data/captura_v6/AAAA-MM-DD.json (NÃO usar fetch_literature*.py)
python3 scripts/importar_v6.py

# 2. Triagem, classificação de prioridades e síntese transversal dinâmica (gera edicao_atual.json e atualiza __EMBEDDED_DATA__)
python3 scripts/reclassificar.py

# 3. Enriquecimento profundo dos 5 blocos com Gemini 3.8 Flash
python3 scripts/enriquecer_tudo_flash38.py

# 4. Geração da transcrição limpa para Eleven Reader (rápido) ou transcrição + MP3 fallback
python3 scripts/gerar_podcast_28min.py --somente-texto
# (Opcional com MP3 Edge-TTS fallback: python3 scripts/gerar_podcast_28min.py)

# 5. Commit e deploy no GitHub Pages
git add data/ index.html audio/ scripts/
git commit -m "feat(rotina): screening diário, conexões transversais e roteiro Eleven Reader atualizados [skip ci]"
git push origin main
```

---

## 6. Governança da Interface Web (`index.html`)

O arquivo `index.html` deve manter rigorosamente a arquitetura de faixas em largura total na aba **Pauta**:
1. **Faixa 1 — Topo da Pauta (`.pauta-topo`)**:
   - Grid assimétrico (`1.45fr` Panorama à esquerda | `1fr` `.lado` à direita com Horizonte Lateral, Pendências, Para ver e ouvir, De olho) encerrando-se acima do bloco de áudio para evitar vazios verticais no restante da página.
2. **Faixa 2 — Áudio (Eleven Reader) & Dossiê de Conexões Transversais Lado a Lado (`.audio-sintese-dupla`, largura total `.wrap`)**:
   - **Coluna 1 (Áudio & Eleven Reader, `0.92fr`)**:
     - Título dinâmico: `Podcast de Bancada & Stork Cast — {dataExtensa(podcastIso)}`.
     - Destaque principal ao **Eleven Reader** + botão `[📋 Copiar Transcrição (Eleven Reader)]` (`copiarTranscricaoPodcast(btn, podcastIso)` com fallback de cópia sem depender apenas de `navigator.clipboard`).
     - Links de apoio: `[📄 Abrir Roteiro TXT]` e `[⬇ MP3 Fallback]`, além do botão secundário `[▶ Player Local (Edge-TTS)]`.
   - **Coluna 2 (Conexões Transversais & Análise do Podcast, `1.58fr`)**:
     - Bloco `.sintese-transversal-box` com grade 2×2 (`.sintese-eixos-grid`) renderizada dinamicamente a partir de `p.conexoes_transversais`.
     - Cada cartão mostra título, evidência com revista/PMID real, aplicação `Na nossa bancada` e chips clicáveis (`artigos_ref` chamando `abrirLeitor(id)` e selo `horizonte_lateral` chamando `trocar("fronteira")`).
3. **Faixa 3 — Listas de Artigos em Duas Colunas em Largura Total (`.fichas.fichas-duas-colunas`)**:
   - Tanto **"o que ler antes da reunião"** quanto **"mais trabalhos em circulação nesta semana"** renderizam em `section.wrap.secao` usando `.fichas.fichas-duas-colunas` (`grid-template-columns: repeat(2, minmax(0, 1fr)) !important;` acima de `860px`, 1 coluna no mobile), com cartões esticados em altura uniforme.
4. **Leitor Modal de Fichas (`abrirLeitor`) & Aba Horizonte Lateral**:
   - Exibição estruturada dos 5 blocos de análise, links com selo de Acesso Aberto/Assinatura e consulta Gemini 3.8 Flash.
   - Aba **Horizonte Lateral** renderizada integralmente a partir de `radar_cultural` com todos os campos de interseção com o LUCHM preenchidos.
