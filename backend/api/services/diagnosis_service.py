import logging

from sqlalchemy.orm import Session

from backend.api.services.telemetry_service import TelemetryService
from backend.ml.feature_extractor import FeatureExtractor
from backend.ml.model_loader import ModelLoader


logger = logging.getLogger("motorguard.backend.diagnosis")


class DiagnosisService:

    def __init__(
        self,
        session: Session,
        influx_store,
        model_loader: ModelLoader,
    ):
        self.telemetry_service = TelemetryService(
            session=session,
            influx_store=influx_store,
        )

        self.model_loader = model_loader

    def diagnose(
        self,
        factory_id: str,
        motor_id: str,
    ) -> dict:

        # --------------------------------------------------
        # 1. Retrieve the latest motor telemetry
        # --------------------------------------------------

        telemetry = self.telemetry_service.get_latest(
            factory_id=factory_id,
            motor_id=motor_id,
        )

        if telemetry is None:
            raise LookupError(
                "No telemetry available for this motor"
            )

        # --------------------------------------------------
        # 2. Extract and validate ML features
        # --------------------------------------------------

        features = FeatureExtractor.extract(
            telemetry
        )

        # --------------------------------------------------
        # 3. Retrieve the already-loaded model
        # --------------------------------------------------

        model = self.model_loader.get_model()

        # --------------------------------------------------
        # 4. Perform classification
        # --------------------------------------------------

        prediction = model.predict([features])

        predicted_class = str(prediction[0])

        # --------------------------------------------------
        # 5. Calculate optional confidence
        # --------------------------------------------------

        confidence = None

        if hasattr(model, "predict_proba") and hasattr(model, "classes_"):

            probabilities = model.predict_proba(
                [features]
            )[0]

            model_classes = list(model.classes_)

            try:
                class_index = model_classes.index(
                    prediction[0]
                )

                confidence = float(
                    probabilities[class_index]
                )

            except (ValueError, IndexError):
                logger.warning(
                    "Could not map predicted class to probability"
                )

        # --------------------------------------------------
        # 6. Return diagnosis
        # --------------------------------------------------

        result = {
            "factory_id": telemetry["factory_id"],
            "line_id": telemetry["line_id"],
            "motor_id": telemetry["motor_id"],
            "timestamp": telemetry["timestamp"],
            "predicted_class": predicted_class,
            "confidence": confidence,
            "ground_truth": telemetry.get("ground_truth"),
            "is_simulated": telemetry.get("is_simulated"),
        }

        logger.info(
            "Motor diagnosis completed | factory=%s | motor=%s | prediction=%s | confidence=%s",
            factory_id,
            motor_id,
            predicted_class,
            confidence,
        )

        return result