---
name: rankeamento-noticias
description: Avaliar a relevância editorial de um dossiê jornalístico apurado, atribuindo score e recomendação de publicação com base em impacto, alcance, confiabilidade e potencial informativo.
metadata:
  version: "1.0.0"
  tags: ["jornalismo", "ranking", "relevancia", "editorial", "decisao"]
---

# Avaliação de Relevância Editorial (Ranker)

Avalie um dossiê jornalístico estruturado e determine sua relevância editorial, atribuindo um score e uma recomendação.

---

## Quando usar

- Após a etapa de apuração de fontes
- Quando for necessário decidir se um evento merece cobertura jornalística
- Para priorizar ou validar a produção de uma matéria

---

## Entrada esperada

Um dossiê estruturado contendo:

- EVENTO PRINCIPAL
- AVALIAÇÃO PRELIMINAR DE RELEVÂNCIA
- (opcional) NÍVEL DE CONFIANÇA
- FONTES COLETADAS
- LINHA DO TEMPO
- PONTOS DE CONSENSO
- CONTRADIÇÕES E DIVERGÊNCIAS
- LACUNAS

---

## Processo

1. **Compreender o evento**
   - O que aconteceu?
   - Quem são os envolvidos?
   - Onde e quando ocorreu?

2. **Avaliar impacto**
   - Econômico, político, social, tecnológico ou internacional
   - Número de pessoas ou setores afetados

3. **Avaliar alcance**
   - Local, nacional ou global

4. **Avaliar qualidade da apuração**
   - Número de fontes
   - Consistência entre fontes
   - Presença de contradições
   - Lacunas relevantes

5. **Avaliar confiabilidade**
   - Baseado no nível de consenso e na qualidade das fontes

6. **Avaliar potencial jornalístico**
   - Há desdobramentos possíveis?
   - É um tema que exige acompanhamento?
   - Tem valor informativo relevante para o público?

7. **Atribuir score final (0 a 10)**

---

## Critérios de avaliação

Considere os seguintes eixos:

- Impacto (peso alto)
- Alcance (peso médio)
- Atualidade (peso médio)
- Confiabilidade (peso alto)
- Clareza do evento (peso médio)
- Potencial de desdobramento (peso médio)

---

## Formato de saída (OBRIGATÓRIO)

Retorne APENAS um JSON válido no seguinte formato:

{
  "score": 0.0,
  "classification": "alta",
  "decision": "publicar",
  "priority": "alta",
  "justification": "string",
  "attention_points": [
    "string",
    "string"
  ]
}

---

## Regras IMPORTANTES

- Não inventar informações — baseie-se apenas no dossiê
- Seja consistente com os dados apresentados
- Não reescreva o dossiê
- Não introduza fatos novos
- A decisão deve ser justificável a partir das evidências
- classification deve ser exatamente: "alta", "media" ou "baixa"
- decision deve ser exatamente: "publicar", "publicar_com_ressalvas" ou "nao_publicar"
- priority deve ser exatamente: "alta", "media" ou "baixa"
- justification deve ter entre 3 e 6 frases
- Retorne SOMENTE o JSON (sem texto antes ou depois)
- Não use markdown (sem ```json)
- attention_points deve conter de 1 a 3 itens

---

## Regras de consistência

- Score >= 8 → classification deve ser "alta"
- Score entre 5 e 7.9 → "media"
- Score < 5 → "baixa"

- Se classification for "alta" → priority deve ser "alta"
- Se classification for "media" → priority deve ser "media"
- Se classification for "baixa" → priority deve ser "baixa"

- Se classification for "baixa" → decision deve ser "nao_publicar"

---

## Objetivo

Garantir que apenas eventos com relevância editorial adequada avancem para:

- verificação factual
- redação da matéria

Atuando como filtro de qualidade e priorização jornalística