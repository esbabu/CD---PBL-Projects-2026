"""Back up and retrain the persisted classifier with the installed scikit-learn."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sys

import sklearn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from error_classifier import ErrorClassifier  # noqa: E402


def main() -> None:
    classifier = ErrorClassifier()
    model_path = Path(classifier.model_file)
    if model_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = model_path.with_name(f"{model_path.stem}.{timestamp}{model_path.suffix}")
        shutil.copy2(model_path, backup_path)
        print(f"Backed up existing model to {backup_path}")

    print(f"Retraining with scikit-learn {sklearn.__version__}")
    classifier.train_and_save()
    print(f"Saved refreshed model to {model_path}")


if __name__ == "__main__":
    main()