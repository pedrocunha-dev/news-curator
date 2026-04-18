# News Curator

An AI-powered news curation pipeline that researches, investigates, fact-checks, and writes a full journalistic article on any topic you provide — all automatically.

Built with the [agno](https://github.com/agno-agi/agno) multi-agent framework and OpenAI's GPT models, the pipeline simulates a complete newsroom: a research team, an investigative reporter, an editorial gate, a fact-checker, and a writer, all working in sequence.

---

## How it works

When you enter a topic, the pipeline runs through six stages:

```
Topic → Research → Investigation (loop) → Ranking → Editorial Gate → Fact-check → Writing → Article
```

| Stage | What happens |
|---|---|
| **Research** | A team of agents searches the web for the most relevant and recent news on the topic |
| **Investigation** | An agent collects at least 3 independent sources; retries up to 3 times if the minimum isn't met |
| **Ranking** | An editorial agent scores the story (relevance, reliability, impact) and decides whether to publish |
| **Editorial Gate** | A programmatic check reads the ranking decision — if `nao_publicar`, the pipeline stops |
| **Fact-check** | An agent cross-references all facts across sources and flags disputed or unverified claims |
| **Writing** | A journalist agent produces a 400–600 word article in Brazilian Portuguese with full source references |

Each run saves its files in an isolated subfolder under `output/<run_id>/`, so multiple searches never interfere with each other.

---

## Interface

The project includes a **Streamlit web UI** — no command line required for everyday use.

![Pipeline in action](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat&logo=streamlit)

Just type a topic and wait. The UI shows the pipeline progress step by step and displays the final article with download buttons for all generated files.

---

## Project structure

```
news-curator/
│
├── app.py                        # Streamlit web interface
├── main.py                       # CLI entry point
│
├── agents/
│   └── curator_agent.py          # Pipeline orchestration (run_agent, run_agent_stream)
│
├── core/
│   ├── agents_factory.py         # Creates all AI agents and teams
│   ├── workflow_factory.py       # Assembles the agno Workflow with all steps
│   ├── loop_utils.py             # Source-counting logic for the investigation loop
│   └── ranker_utils.py           # Editorial gate: reads ranking JSON and decides
│
├── infrastructure/
│   ├── skills_loader.py          # Loads skill files at runtime
│   └── tools_factory.py          # Configures FileTools for each run's isolated folder
│
├── config/
│   └── settings.py               # Constants and API key loading
│
├── skills/                       # Skill instructions loaded by agents at runtime
│   ├── pesquisa-noticias/
│   ├── apuracao-fontes/
│   ├── rankeamento-noticias/
│   ├── verificacao-factual/
│   └── redacao-jornalistica/
│
└── output/                       # Generated files (git-ignored)
    └── <run_id>/
        ├── pesquisa_<event_id>_<date>.json
        ├── apuracao_<event_id>_<date>.md
        ├── ranking_<event_id>_<date>.json
        ├── verificacao_<event_id>_<date>.md
        └── materia_<event_id>_<date>.md
```

---

## Requirements

- Python 3.12.11
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/pedrocunha-dev/news-curator.git
cd news-curator
```

**2. Create and activate a virtual environment**

```bash
# With uv (recommended)
uv venv --python 3.12.11
source .venv/bin/activate
uv sync

# Or with standard pip
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Set up your API key**

Create a `.env` file at the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

> **Never commit this file.** It is already listed in `.gitignore`.

---

## Running the web interface

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`, type a topic, and the pipeline will run automatically.

---

## Running from the command line

```bash
python main.py "your topic here"
```

Example:

```bash
python main.py "Brazil central bank raises interest rates"
```

---

## Configuration

All pipeline constants are in `config/settings.py`:

| Constant | Default | Description |
|---|---|---|
| `MIN_FONTES` | `3` | Minimum sources required before the investigation loop exits |
| `MAX_TENTATIVAS_APURACAO` | `3` | Maximum retries for the investigation loop |

All agents use the `gpt-5-nano` model via the OpenAI Responses API.

---

## Skills system

Each pipeline stage is guided by a **skill** — a Markdown file that instructs the agent on exactly what to do, what format to output, and what rules to follow. Skills live in `skills/<name>/SKILL.md` and are loaded at runtime.

| Skill | Output format |
|---|---|
| `pesquisa-noticias` | Pure JSON (7 fields) |
| `apuracao-fontes` | Markdown (8 sections) |
| `rankeamento-noticias` | Pure JSON (6 fields) |
| `verificacao-factual` | Markdown (7 sections) |
| `redacao-jornalistica` | Markdown article (400–600 words) |

---

## Output files

Every run generates up to 5 files inside `output/<run_id>/`:

| File | Contents |
|---|---|
| `pesquisa_<event_id>_<date>.json` | Research result: title, summary, source, URL, keywords, event ID |
| `apuracao_<event_id>_<date>.md` | Investigation dossier with all sources collected |
| `ranking_<event_id>_<date>.json` | Editorial score, classification, and publish decision |
| `verificacao_<event_id>_<date>.md` | Fact-check report: confirmed, disputed, and unverified facts |
| `materia_<event_id>_<date>.md` | Final journalistic article ready for publication |

Files from different runs are stored in separate subfolders and never overwrite each other.

---

## Security

- **Never commit your `.env` file.** It contains your API key and is git-ignored by default.
- Before pushing, verify with `git ls-files .env` — if the output is empty, you are safe.

---

## Tech stack

| Library | Role |
|---|---|
| [agno](https://github.com/agno-agi/agno) | Multi-agent workflow orchestration |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | LLM calls via Responses API |
| [Streamlit](https://streamlit.io) | Web interface |
| [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) | Web search tool for agents |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable loading |
| [uv](https://github.com/astral-sh/uv) | Dependency management |

---

## License

This project is open source. Feel free to use, adapt, and contribute.
