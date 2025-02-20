from pathlib import Path

from loguru import logger
from tqdm import tqdm

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

REPO_ROOT = Path(__file__).absolute().parent.parent.parent
LOG_DIR = REPO_ROOT / "logs"


class DataPath:
    BASE_DIR = REPO_ROOT / "data"
    RAW_DIR = BASE_DIR / "1-raw"
    PROCESSED_DIR = BASE_DIR / "2-processed"
    RAW_POLYGONS = RAW_DIR / "polygons.parquet"
    RAW_PLACES_DIR = RAW_DIR / "places"
    RAW_CLASSROOMS = RAW_DIR / "classrooms.parquet"
    OCCUPANCY = PROCESSED_DIR / "occupancy.parquet"
    CLASSROOMS = PROCESSED_DIR / "classrooms.parquet"
    SCHEDULE = PROCESSED_DIR / "schedule.parquet"


OCCUPANCY_URL = (
    "https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
)
