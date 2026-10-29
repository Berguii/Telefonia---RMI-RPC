
import logging
from pathlib import Path

# Cria uma pasta para guardar os registros
PASTA_LOGS = Path("logs")
PASTA_LOGS.mkdir(exist_ok=True)

# Configura o sistema de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            PASTA_LOGS / "servidor.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

# Logger utilizado pelo servidor
logger = logging.getLogger("telefonia")
