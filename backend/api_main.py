
import uvicorn

from backend.logging_config import configure_logging


def main():
    configure_logging()

    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
