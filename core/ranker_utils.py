import json
import os
import re

# Porteiro editorial do pipeline: lê o arquivo de ranking mais recente e decide
# se a notícia deve seguir para publicação (True) ou ser barrada (False).
def deve_publicar(_, output_dir: str = "output"):
    try:
        pasta_output = output_dir

        # Lista apenas os arquivos JSON cujo nome contém "rank" (ex: ranking_*.json).
        arquivos = [
            f for f in os.listdir(pasta_output)
            if f.endswith(".json") and "rank" in f
        ]

        # Se nenhum arquivo de ranking existir, não há base para decisão: barra a publicação.
        if not arquivos:
            return False

        # Ordena os nomes em ordem decrescente. Como os nomes incluem a data (YYYY-MM-DD),
        # a ordenação alfabética coincide com a cronológica — o mais recente fica no índice 0.
        arquivos.sort(reverse=True)
        arquivo = arquivos[0]

        # Monta o caminho completo: "output/ranking_<event_id>_<data>.json"
        caminho = os.path.join(pasta_output, arquivo)

        # Lê todo o conteúdo do arquivo como texto.
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Tenta parse direto; se falhar, usa regex para extrair o campo 'decision'
        try:
            # Plano A: o agente gerou JSON limpo — parse direto.
            resultado = json.loads(conteudo)
            decision = resultado.get("decision", "")
        except json.JSONDecodeError:
            # Plano B: o JSON veio "sujo" (ex: envolto em ```json ... ```).
            # O regex localiza o padrão "decision": "valor" diretamente no texto bruto.
            match = re.search(r'"decision"\s*:\s*"([^"]+)"', conteudo)
            if not match:
                print("Erro ao ler ranking: campo 'decision' não encontrado")
                return False
            # .group(1) retorna o conteúdo capturado dentro dos parênteses do regex.
            decision = match.group(1)

        # Retorna True apenas para decisões que autorizam publicação;
        # qualquer outro valor (ex: "nao_publicar") encerra o pipeline.
        return decision in ["publicar", "publicar_com_ressalvas"]

    except Exception as e:
        print(f"Erro ao ler ranking: {e}")
        return False