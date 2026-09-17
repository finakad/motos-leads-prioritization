from dataclasses import dataclass
from pathlib import Path


class SourceFileError(Exception):
    """Raised when a source file cannot be processed safely."""


class RowValidationError(Exception):
    """Raised when a source row contains invalid required data."""


@dataclass(frozen=True)
class LoadResult:
    """Summarizes a loader execution."""

    records_received: int
    records_processed: int
    records_rejected: int


def get_raw_data_path(file_name: str) -> Path:
    """Returns a source file path inside data/raw."""

    backend_dir = Path(__file__).resolve().parents[2]
    file_path = backend_dir / "data" / "raw" / file_name

    if not file_path.is_file():
        raise SourceFileError(f"Source file was not found: {file_path}")

    return file_path