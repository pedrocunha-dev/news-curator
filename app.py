import io
import zipfile
from pathlib import Path

import streamlit as st


def main():
    st.set_page_config(page_title="Curador de Notícias", page_icon="📰", layout="centered")
    st.title("📰 Curador de Notícias")
    st.caption("Curadoria jornalística automatizada. Digite um tema e aguarde a matéria.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "output_files" not in st.session_state:
        st.session_state.output_files = {}
    if "is_running" not in st.session_state:
        st.session_state.is_running = False

    if st.session_state.messages and not st.session_state.is_running:
        if st.button("🗑️ Limpar conversa", use_container_width=False):
            st.session_state.messages = []
            st.session_state.output_files = {}
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.output_files and not st.session_state.is_running:
        _render_downloads(st.session_state.output_files)

    prompt = st.chat_input(
        "Digite o tema da notícia...",
        disabled=st.session_state.is_running,
    )
    if prompt:
        _handle_input(prompt)


def _handle_input(topic: str):
    from agents.curator_agent import run_agent_stream

    st.session_state.output_files = {}
    st.session_state.is_running = True

    st.session_state.messages.append({"role": "user", "content": topic})
    with st.chat_message("user"):
        st.markdown(topic)

    materia = None
    stopped = False
    stop_reason = None
    run_dir = None

    STEP_ORDER = [
        "pesquisa", "apuracao_loop", "rankeamento",
        "gate_editorial", "verificacao", "redacao",
    ]
    STEP_TOTAL = len(STEP_ORDER)

    with st.chat_message("assistant"):
        st.markdown(
            "⏳ **Curadoria em andamento — isso pode levar alguns minutos.**\n\n"
            "Não feche a página. Estou pesquisando, apurando e redigindo a matéria para você."
        )
        progress_bar = st.progress(0, text="Iniciando pipeline...")
        status_box = st.empty()
        result_box = st.empty()

        step_count = 0

        try:
            for event_type, content in run_agent_stream(topic):
                if event_type == "run_dir":
                    run_dir = Path(content)
                elif event_type == "progress":
                    step_count += 1
                    pct = int((step_count / STEP_TOTAL) * 90)
                    progress_bar.progress(pct, text=content)
                    status_box.info(content)
                elif event_type == "materia":
                    materia = content
                elif event_type == "parado":
                    stopped = True
                    stop_reason = content
        except Exception as exc:
            progress_bar.empty()
            status_box.empty()
            result_box.error(f"Erro no pipeline: {exc}")
            st.session_state.is_running = False
            return

        progress_bar.empty()
        status_box.empty()

        if stopped:
            final = f"⛔ **Notícia não aprovada para publicação.**\n\n{stop_reason or ''}"
            result_box.markdown(final)
            st.session_state.messages.append({"role": "assistant", "content": final})
        elif materia:
            result_box.markdown(materia)
            st.session_state.messages.append({"role": "assistant", "content": materia})
            st.session_state.output_files = _collect_run_files(run_dir) if run_dir else {}
        else:
            final = "⚠️ Pipeline concluído, mas a matéria não foi gerada."
            result_box.warning(final)
            st.session_state.messages.append({"role": "assistant", "content": final})

    st.session_state.is_running = False
    st.rerun()


def _collect_run_files(run_dir: Path) -> dict:
    if not run_dir.exists():
        return {}

    patterns = [
        ("Pesquisa", "pesquisa_*.json"),
        ("Apuração", "apuracao_*.md"),
        ("Ranking", "ranking*.json"),
        ("Verificação", "verificacao_*.md"),
        ("Matéria", "materia_*.md"),
    ]

    files = {}
    for label, pattern in patterns:
        matches = list(run_dir.glob(pattern))
        if matches:
            files[label] = max(matches, key=lambda f: f.stat().st_mtime)

    return files


def _render_downloads(files: dict):
    st.divider()
    st.subheader("📁 Arquivos gerados")

    cols = st.columns(len(files))
    for col, (label, path) in zip(cols, files.items()):
        col.download_button(
            label=f"📄 {label}",
            data=path.read_bytes(),
            file_name=path.name,
            mime="application/octet-stream",
            use_container_width=True,
        )

    st.download_button(
        label="📦 Baixar tudo (ZIP)",
        data=_create_zip(files),
        file_name="news_curator_output.zip",
        mime="application/zip",
        use_container_width=True,
        type="primary",
    )


def _create_zip(files: dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, path in files.items():
            zf.write(path, path.name)
    return buffer.getvalue()


if __name__ == "__main__":
    main()
