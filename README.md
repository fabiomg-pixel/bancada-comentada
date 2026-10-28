# Bancada Comentada 🔬📖

Revista digital de literatura científica e leitura conjunta do laboratório (**PlasmoVet / IBCCF / UFRJ**).

Site publicado via GitHub Pages:  
👉 **[https://fabiomg-pixel.github.io/bancada-comentada/](https://fabiomg-pixel.github.io/bancada-comentada/)**

---

## 🎯 Como Funciona

1. **Varredura e Ingestão Diária:**  
   A rotina de inteligência do laboratório (*Resumo da Literatura Científica v6*) varre o PubMed e bioRxiv em 5 eixos temáticos:
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
* `data/interacoes.json`: Marcações sincronizadas da equipe (catálogo, sinais, anotações).
* `data/edicao_atual.json`: Cópia de referência dos metadados completos dos artigos em circulação.
* `scripts/sync_lab.py`: Ponte de automação com o laboratório e o Second Brain.
