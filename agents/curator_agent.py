# =============================================================================
# Agente Curador de Notícias (Workflow com Team e Loops)
# =============================================================================
#
# Este script cria um WORKFLOW COMPLETO de IA que atua como uma redação jornalística.
# Ele recebe um tema e coordena diferentes agentes e equipes em etapas distintas:
#
#   TEMA → Pesquisa (Team) → Apuração (Loop) → Ranker → Verificação → Redação → Matéria Final (.md)
#
# Conceitos praticados:
#   • Team      — uma equipe de agentes trabalhando juntos sob a coordenação de um líder
#   • Workflow  — orquestração do fluxo de trabalho dividindo o processo em etapas (Steps)
#   • Loop      — repetição de um Step até que uma condição específica (end condition) seja atingida
#   • Skills    — habilidades carregadas a partir de arquivos externos e compartilhadas
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTAÇÕES E CONFIGURAÇÕES INICIAIS
# Carregamos as bibliotecas necessárias para o Workflow, Agents, Teams e Utils.
# ─────────────────────────────────────────────────────────────────────────────

from pathlib import Path

from infrastructure.skills_loader import load_skills
from infrastructure.tools_factory import create_file_tools
from core.agents_factory import create_agents
from core.workflow_factory import create_workflow

from agno.workflow import Workflow

from core.ranker_utils import deve_publicar

_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

_STEP_LABELS = {
    "pesquisa": "🔍 Pesquisando notícias...",
    "apuracao": "📋 Apurando fontes...",
    "apuracao_loop": "📋 Apurando fontes...",
    "rankeamento": "⚖️ Rankeando relevância editorial...",
    "gate_editorial": "🚦 Verificando critérios editoriais...",
    "verificacao": "🔎 Verificando fatos...",
    "redacao": "✍️ Redigindo a matéria...",
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÃO DE EXECUÇÃO
# Definição da função que inicializa o processo.
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(topic: str):
    skills = load_skills()
    file_tools = create_file_tools()
    agents = create_agents(skills, file_tools)

    workflow = create_workflow(agents)

    print("\n📌 Etapas do workflow:")
    for i, step in enumerate(workflow.steps):
        print(i, step.name)

    print("\n🚀 Executando pipeline completo...\n")

    result = workflow.run(topic)

    print("\n─── RESULTADO DO PIPELINE ───")
    if hasattr(result, "steps"):
        for step_output in result.steps or []:
            name = getattr(step_output, "step_name", "?")
            content = getattr(step_output, "content", "")
            stopped = getattr(step_output, "stop", False)
            preview = str(content)[:300].replace("\n", " ") if content else "(sem conteúdo)"
            status = "🛑 STOP" if stopped else "✅"
            print(f"\n{status} [{name}]\n{preview}...")
    else:
        content = getattr(result, "content", str(result))
        print(str(content)[:500])


def run_agent_stream(topic: str):
    """Generator that yields (type, content) tuples for UI integration.

    Yields:
        ("run_dir", path_str) — isolated output directory for this run
        ("progress", label_str) — pipeline step started
        ("parado", reason_str) — gate editorial rejected the story
        ("materia", markdown_str) — final article content
    """
    import uuid
    from agno.run.workflow import StepStartedEvent, StepOutputEvent

    run_id = str(uuid.uuid4())[:8]
    run_dir = _OUTPUT_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    yield ("run_dir", str(run_dir))

    skills = load_skills()
    file_tools = create_file_tools(run_dir)
    agents = create_agents(skills, file_tools)
    workflow = create_workflow(agents, str(run_dir))

    # Force a fresh session per call so agno never replays a cached result.
    events = workflow.run(topic, stream=True, session_id=str(uuid.uuid4()))

    seen_steps: set = set()
    stopped = False

    for event in events:
        if isinstance(event, StepStartedEvent):
            name = getattr(event, "step_name", "")
            if name and name not in seen_steps and name in _STEP_LABELS:
                seen_steps.add(name)
                yield ("progress", _STEP_LABELS[name])

        elif isinstance(event, StepOutputEvent):
            if getattr(event, "stop", False):
                reason = getattr(event, "content", "") or "Notícia não passou no gate editorial."
                yield ("parado", reason)
                stopped = True

    if not stopped:
        materia_files = list(run_dir.glob("materia_*.md"))
        if materia_files:
            latest = max(materia_files, key=lambda f: f.stat().st_mtime)
            yield ("materia", latest.read_text(encoding="utf-8"))