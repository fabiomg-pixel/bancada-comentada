# Bancada Comentada 🔬📖

Revista digital de literatura científica e leitura conjunta do laboratório (**PlasmoVet / IBCCF / UFRJ**).

Site publicado via GitHub Pages:  
👉 **[https://fabiomg-pixel.github.io/bancada-comentada/](https://fabiomg-pixel.github.io/bancada-comentada/)**

---

## 🎯 Como Funciona

> **Revista oficial e espelho (desde 09/11/2026).** A revista oficial do grupo é a do claude.ai, alimentada pela rotina *Resumo da Literatura Científica v6*. Esta página é o **espelho** dela: não faz captura própria. Em dias úteis, a tarefa agendada *Espelho da Bancada no GitHub* grava o depósito do dia em `data/captura_v6/AAAA-MM-DD.json`; o push dispara a rotina deste repositório, que importa esses artigos (`scripts/importar_v6.py`), faz o enriquecimento em 5 blocos e gera o podcast. `scripts/fetch_literature.py` fica no repositório só como histórico e não roda.

1. **Varredura e Ingestão Diária:**  
   A rotina de inteligência do laboratório (*Resumo da Literatura Científica v6*) varre o PubMed e bioRxiv em 5 eixos temáticos e deposita na revista do claude.ai; o espelho recebe o mesmo depósito:
   * 🧠 **Cérebro** (patogênese, malária cerebral, neuroimunologia)
   * 🦟 **Vetor** (Aedes, Anopheles, competência vetorial)
   * 🛡️ **Hospedeiro** (resposta imune, autofagia, inflamação)
   * 🔄 **Ciclo** (diferenciação, transmissão, esporogonia)
   * 🛠️ **Métodos** (protocolos experimentais, microscopia, bioinformática)

2. **Leitura e Gestão Conjunta:**  
   Na página web da revista, os pesquisadores e estudantes podem:
   * 🏷️ **Catalogar:** Marca o artigo como parte permanente do acervo do laboratório (nunca expira no ciclo de 14 dias).
   * 🔖 **Sinalizar Leitura:** *"Quero ler"*, *"Lido / Arquivado"* ou criar ficha.
   * 📝 **Anotações de Bancada:** Selecione qualquer trecho do texto para destacar achados, métodos, limitações ou dúvidas com comentários do grupo.
   * 🎙️ **Clube de Leitura:** Visualizar e assumir a escala de seminários de sexta-feira.

3. **Ciclo de Feedback para o Laboratório e Second Brain (Logseq):**  
   * **No Navegador:** Clique em `Sincronizar` (botão no cabeçalho) para enviar as escolhas para o GitHub ou baixar o pacote `interacoes.json`.
   * **No Ambiente Local do Lab:** Execute:
     ```bash
     python3 scripts/sync_lab.py
     ```
     O script automaticamente:
     * Puxa as marcações atualizadas da web;
     * Gera ou atualiza as páginas no seu grafo do **Logseq** (`second-brain/pages/@citekey.md`);
     * Preenche as anotações, métodos em destaque e backlinks de conceitos automaticamente;
     * Commita e sincroniza o seu Second Brain no GitHub!

---

## 🚀 Estrutura do Repositório

* `index.html`: A revista digital completa e interativa (executada no GitHub Pages).
* `data/captura_v6/`: Depósito diário da v6 vindo da revista do claude.ai — a única entrada de literatura do espelho.
* `scripts/importar_v6.py`: Lê o depósito mais recente e monta `data/literature_capture_raw.json`.
* `data/interacoes.json`: Marcações sincronizadas da equipe (catálogo, sinais, anotações).
* `data/edicao_atual.json`: Cópia de referência dos metadados completos dos artigos em circulação.
* `scripts/sync_lab.py`: Ponte de automação com o laboratório e o Second Brain.
