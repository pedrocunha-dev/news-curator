# CONFIGURAÇÃO DE FERRAMENTAS (TOOLS)

from pathlib import Path
from agno.tools.file import FileTools

# Configuramos o FileTools para salvar e ler arquivos gerados.

def create_file_tools(output_dir: Path):
    return FileTools(
        base_dir=output_dir,
        enable_save_file=True,
        enable_read_file=True,
        enable_list_files=True,
    )

