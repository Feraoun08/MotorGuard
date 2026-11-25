import logging
from pathlib import Path

import joblib

logger = logging.getLogger("motorguard.backend.ml")


class ModelLoader:
    """
    Loads and provides access to the trained fault classification model.

    The model is loaded once during API startup and reused
    for subsequent inference requests.
    """

    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.model = None

    def load(self):
        """
        Load the trained model artifact.
        """

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}"
            )

        logger.info(
            "Loading ML model from %s",
            self.model_path,
        )

        self.model = joblib.load(self.model_path)

        if not hasattr(self.model, "predict"):
            raise TypeError(
                "Loaded model does not implement predict()"
            )

        logger.info(
            "ML model loaded successfully | type=%s",
            type(self.model).__name__,
        )

        return self.model

    def get_model(self):
        """
        Return the loaded model.

        Prevents accidental inference before initialization.
        """

        if self.model is None:
            raise RuntimeError(
                "ML model has not been loaded"
            )

        return self.model