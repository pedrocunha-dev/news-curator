# 5. WORKFLOW STEPS (ETAPAS DO FLUXO)
#    Definição de cada passo individual que o workflow irá executar.

from agno.workflow import Workflow, Step, Loop
from agno.workflow.types import StepOutput

from config.settings import MAX_TENTATIVAS_APURACAO
from core.loop_utils import fontes_suficientes
from core.ranker_utils import deve_publicar

def create_workflow(agents_dict, run_dir: str):
    # Step 1: Pesquisa usando o Team
    pesquisa_step = Step(
        name="pesquisa",
        description="Pesquisa de notícias sobre o tema",
        team=agents_dict["time_research"],
    )

    # Step 2 (Base): Apuração usando o Agente Apurador
    apuracao_step = Step(
        name="apuracao",
        description="Apuração multi-fonte com verificação de fontes",
        agent=agents_dict["apurador"],
    )

    # Step 2 (Loop): Repete a apuração_step até que 'fontes_suficientes' seja True ou
    # atinja o número máximo de tentativas (MAX_TENTATIVAS_APURACAO).
    apuracao_loop = Loop(
        name="apuracao_loop",
        description="Repete a apuração até atingir o mínimo de fontes",
        steps=[apuracao_step],
        max_iterations=MAX_TENTATIVAS_APURACAO,
        end_condition=fontes_suficientes,
    )

    # Step 3: Rankeamento editorial
    rankeamento_step = Step(
        name="rankeamento",
        description="Avaliação de relevância editorial do dossiê",
        agent=agents_dict["rankeador"],
    )

    # Step 3.5: Gate editorial — verifica o JSON do rankeamento antes de prosseguir.
    # Lê 'decision' do arquivo rank_*.json. Se for 'nao_publicar', interrompe o pipeline.
    def gate_executor(step_input):
        if not deve_publicar(step_input, run_dir):
            print("\n🚫 Pipeline encerrado: notícia não passou no filtro editorial.\n")
            return StepOutput(
                content="Pipeline encerrado: notícia não relevante para publicação.",
                stop=True,
            )
        print("\n✅ Gate editorial aprovado: prosseguindo para verificação factual.\n")
        return StepOutput(content="Gate aprovado.")

    gate_step = Step(
        name="gate_editorial",
        description="Filtro editorial: interrompe o pipeline se decision=nao_publicar",
        executor=gate_executor,
    )

    # Step 4: Verificação Factual usando o Agente Verificador
    verificacao_step = Step(
        name="verificacao",
        description="Verificação factual do dossiê",
        agent=agents_dict["verificador"],
    )

    # Step 5: Redação usando o Agente Redator
    redacao_step = Step(
        name="redacao",
        description="Redação jornalística final",
        agent=agents_dict["redator"],
    )

    # CRIAÇÃO DO WORKFLOW
    # Orquestração de todas as etapas definidas acima em uma sequência linear.
    return Workflow(
        name="News Curator Pipeline",
        description="Pesquisa -> Apuração (loop) -> Rankeamento -> Gate -> Verificação -> Redação",
        steps=[
            pesquisa_step,
            apuracao_loop,
            rankeamento_step,
            gate_step,
            verificacao_step,
            redacao_step,
        ],
    )