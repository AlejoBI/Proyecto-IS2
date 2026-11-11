"""Idempotently create MongoDB indexes for deployment and migrations."""

from server.adapters.mongodb_adapter import MongoDBAdapter
from server.app.configurations import Settings


def main() -> None:
    config = Settings()
    MongoDBAdapter(
        uri=config.MONGODB_URI,
        database=config.MONGODB_DATABASE,
        users_collection=config.MONGODB_COLLECTION_USERS,
        documents_collection=config.MONGODB_COLLECTION_DOCUMENTS,
    )
    print("MongoDB indexes ensured")


if __name__ == "__main__":
    main()
