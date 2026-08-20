"""Central configuration and artifact paths."""
from dataclasses import dataclass
from pathlib import Path

DATASET_NAME = "AI-Culture-Commons/ai-culture-multilingual-json-dolma"
DATASET_CONFIG = "json"
DATASET_SPLIT = "train"
LANGUAGES = ("en", "es", "pt")
PROTOTYPE_PER_LANGUAGE = 300
RANDOM_STATE = 42
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384
NORMALIZE_EMBEDDINGS = True

@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem locations used by every pipeline stage."""
    root: Path
    @property
    def models(self) -> Path: return self.root / "models"
    @property
    def dataset(self) -> Path: return self.models / "dataset_procesado.json"
    @property
    def embeddings(self) -> Path: return self.models / "embeddings.npy"
    @property
    def documents(self) -> Path: return self.models / "documents.json"
    @property
    def index(self) -> Path: return self.models / "semantic_index.joblib"
    @property
    def model_config(self) -> Path: return self.models / "model_config.json"
    @property
    def reports(self) -> Path: return self.root / "reports"

def get_paths(root: Path | None = None) -> ProjectPaths:
    """Return project paths without creating artifacts."""
    return ProjectPaths(root or Path(__file__).resolve().parents[2])

def ensure_directories(paths: ProjectPaths) -> None:
    """Create directories required by the pipeline."""
    for directory in (paths.models, paths.root / "data" / "raw", paths.root / "data" / "processed", paths.reports / "eda", paths.reports / "evaluation"):
        directory.mkdir(parents=True, exist_ok=True)
