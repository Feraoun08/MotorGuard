
import logging
import sys


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide logging.
    """

    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid logging level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    # Reduce unnecessary third-party logging noise.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("influxdb_client").setLevel(logging.WARNING)
