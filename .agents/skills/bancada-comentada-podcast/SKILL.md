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

5. **Sincronismo Rigoroso (Screening + Podcast Sempre Juntos)**:
   - Nunca atualizar o screening diário sem atualizar simultaneamente o podcast.
   - O episódio de áudio DEVE cobrir os artigos reais do dia extraídos de `data/edicao_atual.json`. Roteiros estáticos ou congelados são proibidos.

6. **Eleven Reader como Fluxo Principal de Áudio Neural**:
   - Devido a cortes e transições abruptas de cadência entre interlocutores no edge-tts local, o **Eleven Reader** é o canal oficial de síntese de alta fidelidade emocional.
   - A transcrição gerada pelo script deve ser limpa, no formato estrito de diálogo (`Antônio:` e `Francisca:`), pronta para ser colada com um clique via botão de hero no topo da pauta.

7. **Duração do Podcast Calibrada para a Viagem de Carro (25 a 30 Minutos)**:
   - O diálogo deve conter entre **3.500 e 3.850 palavras** distribuídas em ~50 intervenções balanceadas entre Antônio e Francisca.
   - Na cadência neural (~140 palavras/minuto), a duração final deve situar-se estritamente entre **25 e 28 minutos**, correspondendo exatamente ao trajeto de comutação do Prof. Fábio Gomes.

8. **Dossiê de Conexões Transversais Adjacente ao Áudio**:
   - As conexões analíticas e cruzamentos mecanicistas formulados no podcast NÃO podem ficar restritos ao áudio.
   - A interface web DEVE exibir um bloco adjacente ao player (`.audio-sintese-dupla`), contendo o dossiê com os 4 eixos analíticos de bancada (BHE & Morte Endotelial; Vetor & Repasto Sanguíneo; Neuroimunologia & Arrest de CD8+; Biofísica & AFM-IR em nanoescala).

9. **Layout em Duas Colunas para 'O Que Ler Antes da Reunião'**:
   - A seção de destaques prioritários da pauta deve renderizar estritamente em **duas colunas balanceadas** (`.fichas-duas-colunas` com `grid-template-columns: repeat(2, minmax(0, 1fr))`) em telas desktop (>860px), aproveitando plenamente a largura útil da tela e eliminando vazios laterais.

10. **Isolamento de Cache de Áudio**:
   - O diretório temporário de síntese de voz deve ser particionado por dia (`/tmp/luchm_podcast_{hoje}`), prevenindo que resíduos de cache de dias anteriores impeçam a síntese dos novos áudios.

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

## 4. Arquitetura do Podcast (Stork Cast — 25-30 Minutos)

### As Duas Vozes Neurais
* **Antônio (`pt-BR-AntonioNeural`)**: Visão conceitual, fisiopatologia, epidemiologia, imunometabolismo e formulação teórica de hipóteses.
* **Francisca (`pt-BR-FranciscaNeural`)**: Métodos de bancada, protocolos experimentais, controles, microscopia, dissecções e impacto imediato para os alunos e técnicos do LUCHM.

### Estrutura Canônica das 7 Partes do Roteiro Dinâmico
1. **Parte 1 (Abertura & Panorama do Dia)**: Contextualização da data corrente, volume de artigos triados (ex: 81 papers), distribuição de prioridades e contextualização no trânsito (~3.5 min).
2. **Parte 2 (Malária Cerebral & Neuroinflamação)**: Dissecação profunda do paper de malária cerebral do dia ($PbA$, C57BL/6J, MIF, BHE, claudina-5, cinética de dias 4-5) e comparação clínica (~7.5 min).
3. **Parte 3 (Imunidade de Insetos & Membrana Peritrófica)**: Dissecação de barreiras físicas intestinais, microbiota comensal, baculovírus, Cry1Ac e transposição para *Aedes aegypti* (~7.5 min).
4. **Parte 4 (Fisiologia do Vetor & Eixo Gordura-Cérebro)**: Transcriptoma do parasita atravessando barreiras, neuropeptídeo CCHa2, repouso pós-prandial e nosso modelo HFHS (~6.5 min).
5. **Parte 5 (Microscopia Eletrônica de Volume & Impregnação de Metais)**: Protocolo OTO de contrastação pesada, minimização de carga eletrostática e aplicação para acidocalcisomos no CENABIO (~6 min).
6. **Parte 6 (Horizonte Lateral & Ciência de Fronteira)**: O ensaio lateral do mês e a importância de escapar de hipóteses puramente incrementais (~4 min).
7. **Parte 7 (Três Diretrizes Acionáveis de Bancada para Amanhã)**: Três instruções objetivas para o grupo aplicar amanhã cedo no laboratório + encerramento caloroso (~3.5 min).

### Formato de Saída e Distribuição
* `audio/briefing_atual.mp3` e `audio/podcast_comutacao_28min_{hoje}.mp3`: Master MP3 em 192 kbps.
* `audio/briefing_atual.txt` e `audio/podcast_comutacao_28min_{hoje}.txt`: Transcrição integral no formato de diálogo (`Antônio: ...` e `Francisca: ...`).
* `~/Downloads/LUCHM_Podcast_Comutacao_{hoje}.mp3`: Arquivo no Mac para reprodução direta no carro/celular.
* `~/Downloads/LUCHM_Podcast_Transcricao_{hoje}.txt`: Transcrição na pasta Downloads pronta para arrastar ao Eleven Reader.
* Google Drive Stork Podcast: Sincronização em `~/Library/CloudStorage/GoogleDrive-fabiomg@biof.ufrj.br/Meu Drive/Laboratório/LUCHM/Claude Code/stork-podcast/episodes/`.

---

## 5. Fluxo Operacional de Execução Diária

A rotina é disparada autonomamente via GitHub Actions (`rotina_diaria.yml`) ou localmente via linha de comando:

```bash
cd /Users/fabiogomes/.gemini/antigravity/scratch/bancada-comentada

# Executar pipeline completo (Screening + 5 Blocos + Podcast Dinâmico 25 min + Deploy)
python3 scripts/rotina_diaria_completa.py
```

### Se for necessário rodar etapas de forma isolada:
```bash
# 1. Captura calibrada v6 da literatura recente
python3 scripts/fetch_literature.py

# 2. Triagem e classificação de prioridades
python3 scripts/reclassificar.py

# 3. Enriquecimento profundo dos 5 blocos com Gemini 3.8 Flash
python3 scripts/enriquecer_tudo_flash38.py

# 4. Geração do Podcast de 25-30 min e transcrição para Eleven Reader
python3 scripts/gerar_podcast_28min.py

# 5. Commit e deploy no GitHub Pages
git add data/ index.html audio/ scripts/
git commit -m "feat(rotina): screening diário e podcast profundo atualizados [skip ci]"
git push origin main
```

---

## 6. Governança da Interface Web (`index.html`)

O arquivo `index.html` deve manter rigorosamente:
1. **Grid Dupla: Áudio & Dossiê de Conexões Transversais Lado a Lado (`.audio-sintese-dupla`)**:
   - **Coluna 1 (Áudio & Eleven Reader)**:
     - Título dinâmico: `Podcast de Bancada & Stork Cast — {dataExtensa(podcastIso)}`.
     - Cartão informativo destacando o **Eleven Reader** como o gerador prioritário para voz neural ultra-realista sem cortes.
     - Botão `[📋 Copiar Transcrição (Eleven Reader)]`: Aciona `copiarTranscricaoPodcast(btn, podcastIso)` que limpa cabeçalhos e formata os interlocutores (`Antônio:` / `Francisca:`) prontos para o Eleven Reader com feedback visual.
     - Links de apoio: `[📄 Abrir Roteiro TXT]` e `[⬇ Baixar MP3 (25 min)]`.
     - Botão de reprodução instantânea com player persistente dockado na barra inferior do navegador (`toggleAudioPlay()`).
   - **Coluna 2 (Conexões de Bancada & Síntese Transversal)**:
     - Bloco `.sintese-transversal-box` com borda temática destacada.
     - Lista dos 4 eixos analíticos transversais gerados pelo screening e podcast, conectando evidências publicadas na semana aos experimentos concretos do LUCHM (RIPK1 vs Wnt7a; Hemopexina no vetor; Eixo IL-15C/IL-10Rα; AFM-IR e Contactoma).
2. **Layout em Duas Colunas para 'O Que Ler Antes da Reunião'**:
   - Container de destaques com a classe `.fichas.fichas-duas-colunas`.
   - Grid balanceada de 2 colunas no desktop (`grid-template-columns: repeat(2, minmax(0, 1fr)) !important;`) com colapso suave para 1 coluna no mobile (<860px).
3. **Leitor Modal de Fichas (`abrirLeitor`)**:
   - Exibição estruturada dos 5 blocos de análise.
   - Links diretos com selo de Acesso Aberto (PMC / bioRxiv) ou Assinatura (DOI/PubMed).
   - Botão para consultar Gemini 3.8 Flash e salvar notas para o caderno de laboratório (LabELN).
4. **Aba Horizonte Lateral**:
   - Renderização dos cards com selos temáticos (Ensaio, Pesquisador, Tema, Técnica), abrindo o diálogo modal de dossiê completo sem campos em branco.
