# FUNÇÕES AUXILIARES E CONDIÇÕES DE LOOP

#    Neste módulo, introduzimos o conceito de Loop, que permite que o fluxo
#    de trabalho (workflow) repita uma determinada etapa até que alcancemos
#    um critério de sucesso. Para fazer isso, precisamos de:
#    1. Uma métrica de avaliação (função contar_fontes) que diz se a resposta foi boa.
#    2. Uma condição de parada (função fontes_suficientes) que o Loop verifica
#       a cada iteração. Se a condição for atingida, o Loop é encerrado ou 
#       se alcançarmos o número de MAX_TENTATIVAS_APURACAO o loop finaliza.

import re
from typing import List
from agno.workflow.types import StepOutput

from config.settings import MIN_FONTES

def contar_fontes(texto: str) -> int:
    """
    Função Auxiliar: Extração e contagem analítica
    
    Analisa o texto retornado pelo Agente Apurador para contar o número
    de fontes distintas que ele conseguiu encontrar. Para garantir que
    não estejamos contando fontes repetidas apenas pelo título da seção,
    usamos expressões regulares (Regex) para varrer o texto.
    
    Como funciona:
    1. Isola a seção específica ("FONTES COLETADAS") do dossiê.
    2. Conta quantos itens formatados em Markdown (ex: "- **Veículo**") existem.
    3. Conta quantos links web (URLs ou http/https) distintos existem no texto.
    4. Retorna o maior número entre as duas contagens (garantimos assim o pior caso).
    """
    secao = texto
    
    # Passo 1: Captura o conteúdo específico de FONTES COLETADAS através de Regex
    # `re.search`: procura a primeira ocorrência.
    # Padrão: Busca "## FONTES COLETADAS" (com espaços opcionais \s*), captura tudo (.*?)
    #         de forma preguiçosa até encontrar o próximo "##" ou final do texto (##|$).
    # `re.DOTALL`: Faz o `.` capturar também quebras de linha (\n).
    # `re.IGNORECASE`: Ignora maiúsculas/minúsculas.
    # `match.group(1)`: Pega apenas o conteúdo capturado, ignorando os títulos.
    match = re.search(
        r"##\s*FONTES COLETADAS(.*?)(##|$)", texto, re.DOTALL | re.IGNORECASE
    )
    if match:
        secao = match.group(1)

    # Passo 2: Busca listas formatadas padrão Markdown de fontes através de Regex
    # `re.findall`: encontra todas as ocorrências.
    # Padrão `r"^-\s+\*\*"`: Busca início de linha ^, hífen -, um ou mais espaços \s+ 
    #                        e dois asteriscos literais \*\* (indicando negrito no markdown).
    # `re.MULTILINE`: Trata cada nova linha como um novo início para o ^.
    fontes_por_marcador = re.findall(r"^-\s+\*\*", secao, re.MULTILINE)
    
    # Passo 3: Extrai e cria um agrupamento de valores únicos (set) das URLs 
    # encontradas no texto a fim de descartarmos rapidamente links repetidos.
    # Padrão `r"https?://[^\s\)]+"`: Busca links que começam com "http://" ou "https://", 
    #                               seguidos por 1 ou mais caracteres que NÃO sejam espaços
    #                               em branco nem parênteses de fechamento (comum no Markdown).
    # `set(...)`: Cria um conjunto para eliminar automaticamente as URLs duplicadas.
    urls = set(re.findall(r"https?://[^\s\)]+", secao))

    # Retornamos o número máximo capturado, pois alguns links podem não ter o marcador,
    # ou os marcadores não conter links. O maior balanço valida uma contagem sensata.
    return max(len(fontes_por_marcador), len(urls))


def fontes_suficientes(outputs: List[StepOutput]) -> bool:
    """
    Função Condição de Parada (End Condition): Validando o Loop
    
    É utilizada como instrução na etapa de loop da apuração (apuracao_loop).
    Esta função avalia a última resposta (outputs[-1]) obtida e valida
    se atende a regra de negócio da nossa redação: atingir um número
    mínimo predeterminado de fontes.
    
    Funcionamento do fluxo na prática:
    - O Loop de apuração executa a sua tarefa usando o agente correspondente.
    - Essa condição (fontes_suficientes) é executada em seguida por fora, 
      injetando os retornos 'outputs' da execução.
    - Se retornar 'True', o agente atendeu a meta e prossegue para a Verificação Factual.
    - Se retornar 'False', a etapa de apuração ocorre novamente.

    Args:
        outputs (List[StepOutput]): Histórico de respostas/etapas do Workflow anterior
    Returns:
        bool: Retorna True se atingiu ou ultrapassou MIN_FONTES, senão False.
    """
    if not outputs:
        # Se por algum motivo não houver saída do agente anterior, solicitamos nova iteração.
        return False
        
    # Extraímos a resposta obtida pela iteração mais recente do agente (índice [-1])
    latest = outputs[-1]
    
    # Extraímos o conteúdo em texto plano gerado por essa requisição do agente
    content = str(latest.content or "")
    
    # Por fim, passamos o texto final pela função analítica anterior que fará a
    # contagem. Comparamos o resultado usando a constante estática (MIN_FONTES) do topo.
    return contar_fontes(content) >= MIN_FONTES