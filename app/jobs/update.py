from app.api_clients.capital_client import CapitalComClient
from app.db import SessionLocal
from app.services.ingestion import IngestionService
from app.utils.logging import configure_logging


def run() -> None:
    configure_logging()
    db = SessionLocal()
    api_client = CapitalComClient()
    try:
        service = IngestionService(db, api_client)
        service.run_incremental()
    finally:
        api_client.close()
        db.close()


if __name__ == "__main__":
    run()
