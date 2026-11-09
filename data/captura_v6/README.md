# data/captura_v6 — entrada única de literatura do espelho

Um arquivo por dia útil, `AAAA-MM-DD.json`, gravado pela tarefa agendada **Espelho da Bancada no GitHub** a partir do que a rotina *Resumo da Literatura Científica v6* depositou naquele dia na revista do claude.ai (coleção `artigos`, `entrou_em` = o dia). O push de um arquivo novo aqui dispara `.github/workflows/rotina_diaria.yml`.

Formato:

```json
{
  "data": "2026-11-09",
  "origem": "revista do claude.ai — Resumo da Literatura Científica v6",
  "total": 18,
  "artigos": [
    {"pmid": "42811170", "doi": "10.xxxx/yyyy", "titulo": "...", "autores": "...", "revista": "...", "ano": "2026",
     "tipo": "artigo | revisao | preprint | metodo", "resumo": "...", "metodo": "...", "tema": "vetor",
     "importancia": "alta | media | baixa", "prioridade": "essencial | contexto", "implicacao": "...",
     "score": 87, "consulta": "vetores_amplo", "fonte_captura": "Stork | busca própria | preprint",
     "data_fonte": "2026-11-06", "entrou_em": "2026-11-09"}
  ]
}
```

Nada de credencial, dado de pessoa ou marcação de leitura aqui: o repositório é público. As marcas, fichas e anotações do grupo ficam na revista do claude.ai.
