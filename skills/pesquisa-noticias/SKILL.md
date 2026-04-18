---
name: pesquisa-noticias
description: Pesquisar e identificar a notícia mais relevante e atual sobre um tema, fornecendo base estruturada para apuração multi-fonte. Use quando precisar buscar notícias recentes, identificar a notícia principal do dia ou iniciar uma apuração jornalística.
metadata:
  version: "1.0.0"
  tags: ["jornalismo", "pesquisa", "noticias"]
---

# Pesquisa de Notícias

Busque as notícias mais relevantes e recentes sobre um tema e forneça insumos para apuração aprofundada.

## Entrada esperada

- Tema de busca (ex: "política brasileira", "economia", "tecnologia")

## Processo

1. Busque as notícias **mais recentes** sobre o tema
2. Identifique a notícia principal (a mais relevante e atual)
3. Extraia palavras-chave para aprofundamento

## Formato de saída (OBRIGATÓRIO)

Retorne APENAS um JSON válido:

```json
{
  "title": "Título da notícia principal",
  "summary": "Resumo factual em 2-3 frases contendo: (1) o que aconteceu, (2) quem são os atores principais, (3) quando ocorreu (data explícita ou relativa), (4) pelo menos um dado concreto (número, decisão, ação específica). Não inclua opinião ou análise.",
  "source": "Nome do veículo",
  "date": "YYYY-MM-DD",
  "event_id": "string curto identificando o evento (ex: us_iran_war_ceasefire_april_2026)",
  "url": "https://link-da-noticia",
  "keywords": ["termos específicos que permitam encontrar a mesma notícia em outros veículos (inclua nomes próprios, locais, datas ou eventos específicos)"]
}

## Regras

- Priorize notícias do dia atual
- Escolha a notícia com maior impacto e repercussão
- As palavras-chave devem ser específicas o suficiente para encontrar a mesma notícia em outros veículos
- Se não houver notícia clara ou recente, escolha a mais relevante disponível e indique a data corretamente