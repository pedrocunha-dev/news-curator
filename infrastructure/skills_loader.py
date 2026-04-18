# CONFIGURAÇÃO DE SKILLS

from pathlib import Path
from agno.skills import Skills, LocalSkills

# As skills são carregadas localmente de um diretório externo.

def load_skills():
    skills_dir = Path(__file__).resolve().parent.parent / "skills"
    return Skills(loaders=[LocalSkills(str(skills_dir))])