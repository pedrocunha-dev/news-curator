# DEFINIÇÃO DOS AGENTES E EQUIPES
#    Neste módulo, temos vários agentes especializados em papéis distintos.
#    Eles utilizam as skills injetadas e seguem instruções específicas.

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIResponses
from agno.tools.websearch import WebSearchTools

from config.settings import OPENAI_API_KEY, MIN_FONTES

def create_agents(skills, file_tools):

    # 1) Pesquisador — usa a skill de pesquisa de notícias
    pesquisador = Agent(
        name="Pesquisador",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        skills=skills,
        instructions=[
            "Você é um pesquisador de notícias.",
            "Antes de começar, carregue as instruções da skill usando get_skill_instructions.",

            "Execute a skill 'pesquisa-noticias' e retorne EXATAMENTE o JSON abaixo — sem campos extras, sem campos a menos:",
            "Os campos obrigatórios são:",
            "- title: título da notícia principal",
            "- summary: resumo factual em 2-3 frases com o que aconteceu, quem são os atores, quando (data explícita), pelo menos um dado concreto",
            "- source: nome do veículo",
            "- date: data no formato YYYY-MM-DD",
            "- event_id: string curta identificando o evento — ex: russia_ukraine_ceasefire_april_2026 ou us_iran_blockade_april_2026 (crie com base no tema real pesquisado)",
            "- url: URL completa do artigo",
            "- keywords: lista de termos específicos para encontrar a mesma notícia em outros veículos",

            "REGRAS ABSOLUTAS:",
            "- O JSON deve ter EXATAMENTE estes 7 campos: title, summary, source, date, event_id, url, keywords",
            "- NÃO adicione outros campos como 'tema', 'panorama', 'arquivo_salvo_em' ou qualquer outro",
            "- NÃO use objetos aninhados — todos os campos são no nível raiz",
            "- Retorne APENAS o JSON puro, sem texto antes ou depois, sem markdown, sem blocos de código",

            "O resumo deve ser estritamente factual.",
            "Evite termos vagos como 'progresso limitado', 'sem vitória clara', 'situação complexa'.",
            "Sempre inclua pelo menos UM dado concreto (data, número, decisão, ação).",

            "Após formatar o JSON com os 7 campos corretos, salve APENAS esse JSON em arquivo usando a ferramenta de arquivos.",
            "NÃO salve resultados brutos de busca — salve somente o JSON no formato exato.",
            "Use o nome de arquivo no formato: pesquisa_<event_id>_<data_YYYY-MM-DD>.json",
        ],
        tools=[WebSearchTools(), file_tools],
        add_datetime_to_context=True,
        markdown=False,
    )

    # Time de Pesquisa — a equipe lidera e coordena o pesquisador
    time_research = Team(
        name="Research",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        members=[pesquisador],
        instructions=[
            "Você é o líder da equipe de pesquisa.",
            "Sua missão é acionar o Pesquisador UMA ÚNICA VEZ para buscar a notícia mais relevante sobre o tema.",
            "IMPORTANTE: acione o Pesquisador exatamente 1 vez — não repita a busca, não peça confirmação, não valide o resultado.",
            "Após o Pesquisador retornar o JSON e salvar o arquivo, repasse o JSON exatamente como recebido, sem modificações.",
            "Não faça buscas adicionais, não solicite mais detalhes, não peça ao Pesquisador que refaça a tarefa.",
        ],
        add_datetime_to_context=True,
        markdown=True,
    )

    # 2) Apurador de Fontes — usa a skill de apuração multi-fonte
    apurador = Agent(
        name="Apurador de Fontes",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        skills=skills,
        instructions=[
            "Você é um apurador de fontes jornalísticas.",

            "Antes de começar, carregue as instruções da skill usando get_skill_instructions.",

            "Receba a saída do pesquisador e execute a skill 'apuracao-fontes'.",

            f"IMPORTANTE: Você DEVE encontrar no mínimo {MIN_FONTES} fontes distintas.",

            "Se a apuração anterior não atingiu o mínimo, busque fontes DIFERENTES das já encontradas.",

            "Tente outros veículos, incluindo agências internacionais como Reuters, AP e AFP.",

            "Pesquise em inglês e português para ampliar o alcance de fontes.",

            "Siga EXATAMENTE o formato de saída definido na skill 'apuracao-fontes'.",
            "O formato é APENAS Markdown com as seções obrigatórias — sem blocos JSON, sem marcadores extras.",
            "Não adicione texto antes ou depois do dossiê.",

            "Após gerar o dossiê, salve o resultado em um arquivo Markdown (.md) usando a ferramenta de arquivos.",
            "Use o nome de arquivo no formato: apuracao_<event_id>_<data_YYYY-MM-DD>.md",
            "Para obter o event_id: use list_files para listar os arquivos em output/, identifique o arquivo pesquisa_*.json mais recente, use read_file para lê-lo e extraia o campo 'event_id'.",
            "Se não conseguir ler o arquivo, use um resumo descritivo do tema como event_id (ex: russia_ukraine_ceasefire_april_2026).",
        ],
        tools=[WebSearchTools(), file_tools],
        add_datetime_to_context=True,
        markdown=True,
    )

    # 3) Rankeador — avalia relevância editorial do dossiê
    rankeador = Agent(
        name="Rankeador Editorial",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        skills=skills,
        instructions=[
            "Você é um editor responsável por avaliar a relevância de uma notícia.",

            "Antes de começar, carregue as instruções da skill usando get_skill_instructions.",

            "Receba o dossiê do apurador e execute a skill 'rankeamento-noticias'.",

            "IMPORTANTE: Sua resposta DEVE ser um JSON válido.",
            "Não inclua nenhum texto antes ou depois do JSON.",
            "Não use markdown.",
            "Não use comentários.",
            "Não use blocos de código.",

            "O JSON deve conter obrigatoriamente os campos:",
            "score, classification, decision, priority, justification, attention_points",

            "Baseie sua decisão exclusivamente nas evidências do dossiê.",
            "Se houver baixa confiabilidade ou muitas lacunas, reduza o score.",

            "Após gerar o JSON, salve exatamente esse conteúdo em um arquivo usando a ferramenta de arquivos.",
        ],
        tools=[file_tools],
        add_datetime_to_context=True,
        markdown=False,
    )

    verificador = Agent(
        name="Verificador Factual",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        skills=skills,
        instructions=[
            "Você é um verificador factual.",

            "Antes de começar, carregue as instruções da skill usando get_skill_instructions.",

            "Execute a skill 'verificacao-factual' usando o dossiê do apurador presente no histórico.",

            "O formato de saída é APENAS Markdown com as 7 seções obrigatórias definidas na skill:",
            "## FATOS CONFIRMADOS",
            "## FATOS DISPUTADOS RESOLVIDOS",
            "## FATOS DISPUTADOS NÃO RESOLVIDOS",
            "## FATOS NÃO VERIFICADOS",
            "## LACUNAS RESOLVIDAS",
            "## LACUNAS PENDENTES",
            "## ALERTA AO REDATOR",
            "Não inclua blocos JSON, marcadores ou texto fora dessas seções.",

            "OBRIGATÓRIO — SALVAR ARQUIVO:",
            "Após gerar o relatório completo, você DEVE salvar o conteúdo em arquivo .md usando a ferramenta de arquivos.",
            "Use o nome: verificacao_<event_id>_<data_YYYY-MM-DD>.md",
            "O event_id está no campo 'event_id' do JSON do pesquisador — procure no histórico o arquivo pesquisa_*.json ou a mensagem com esse campo.",
            "Se não encontrar o event_id, use um resumo descritivo do tema (ex: cessar_fogo_pascoa_ortodoxa).",
            "NÃO finalize sua resposta sem confirmar que o arquivo foi salvo com sucesso.",
        ],
        tools=[WebSearchTools(), file_tools],
        add_datetime_to_context=True,
        markdown=True,
    )

    # 5) Redator — usa a skill de redação jornalística
    redator = Agent(
        name="Redator",
        model=OpenAIResponses(id="gpt-5-nano", api_key=OPENAI_API_KEY),
        skills=skills,
        instructions=[
            "Você é um redator jornalístico profissional.",

            "Antes de começar, carregue as instruções da skill usando get_skill_instructions.",

            "Execute a skill 'redacao-jornalistica' usando o relatório do verificador factual presente no histórico.",

            "ESTRUTURA OBRIGATÓRIA da matéria (nessa ordem):",
            "1. Título jornalístico (crie um novo — não copie das fontes)",
            "2. Lide: 1 parágrafo respondendo O QUÊ, QUEM, QUANDO, ONDE, POR QUÊ",
            "3. Corpo: 3 a 5 parágrafos em PROSA CORRIDA (pirâmide invertida)",
            "4. Contexto: 1 parágrafo sobre o cenário mais amplo",
            "5. Seção '## Referências' com lista numerada de todas as fontes e URLs",

            "REGRAS INEGOCIÁVEIS:",
            "- NUNCA use bullet points, listas ou seções internas no corpo da matéria",
            "- NUNCA inclua seções de dossiê (Fatos disputados, Lacunas, Nível de confiança, Notas para o redator) — essas são internas e não aparecem na matéria publicada",
            "- SEMPRE cite com [1], [2], [3] cada dado ou fato no corpo",
            "- SEMPRE inclua '## Referências' com URLs completas no final",
            "- Extensão do corpo: 400 a 600 palavras (não contar referências)",
            "- Tom: português brasileiro fluente, sério, imparcial, sem opiniões",

            "Se o JSON do rankeador indicar 'publicar_com_ressalvas':",
            "- Inclua no início: '⚠️ NOTA: Esta matéria apresenta informações com divergências entre fontes.'",
            "- Destaque incertezas de forma natural no corpo, com ressalvas explícitas",

            f"Se houver menos de {MIN_FONTES} fontes no relatório, inclua: '⚠️ NOTA: Esta matéria foi produzida com número limitado de fontes independentes.'",

            "REFERÊNCIAS — regras específicas:",
            "- Cada entrada deve ter: [N] Nome do Veículo — Título exato da matéria. URL completa",
            "- Extraia os títulos e URLs específicas do dossiê de apuração (seção ## FONTES COLETADAS)",
            "- NUNCA use apenas o domínio (ex: https://www.reuters.com) — use a URL completa do artigo",
            "- Exemplo correto: [1] Reuters — What does a US naval blockade of Iran mean for oil flows? https://www.reuters.com/world/middle-east/what-does-us-naval-blockade-iran-mean-oil-flows-2026-04-13/",

            "OBRIGATÓRIO: salve a matéria completa em arquivo Markdown (.md) usando a ferramenta de arquivos.",
            "Use o nome: materia_<event_id>_<data_YYYY-MM-DD>.md",
            "Para obter o event_id: use list_files para listar os arquivos em output/, identifique o arquivo pesquisa_*.json, use read_file para lê-lo e extraia o campo 'event_id'.",
            "ATENÇÃO: o event_id vem do arquivo pesquisa_*.json — nunca use o nome de outro arquivo (verificacao, apuracao, etc.) como base para o event_id.",
            "Se não conseguir ler o arquivo, use um resumo descritivo do tema (ex: russia_ukraine_ceasefire_april_2026).",
            "Nunca termine sem salvar o arquivo.",
        ],
        tools=[file_tools],
        markdown=True,
    )

    return {
        "pesquisador": pesquisador,
        "time_research": time_research,
        "apurador": apurador,
        "rankeador": rankeador,
        "verificador": verificador,
        "redator": redator,
    }