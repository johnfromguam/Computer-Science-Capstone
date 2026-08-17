from pymongo import MongoClient
from pymongo.errors import PyMongoError


class AnimalShelter(object):
    """CRUD operations for the animal collection in MongoDB."""

    def __init__(
        self,
        username,
        password,
        host="localhost",
        port=27017,
        database_name="aac",
        collection_name="animals",
        auth_source="admin",
    ):
        if not username or not password:
            raise ValueError("A MongoDB username and password are required.")

        self.client = MongoClient(
            "mongodb://%s:%s@%s:%d/?authSource=%s"
            % (username, password, host, port, auth_source)
        )
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def create(self, data):
        """Insert one animal record and return True when the insert succeeds."""
        if not isinstance(data, dict) or not data:
            raise ValueError("The data parameter must be a non-empty dictionary.")

        try:
            result = self.collection.insert_one(data)
            return result.inserted_id is not None
        except PyMongoError as error:
            print("Insert failed: %s" % error)
            return False

    def read(self, query=None):
        """Return animal records that match the supplied MongoDB query."""
        if query is None:
            query = {}

        if not isinstance(query, dict):
            raise ValueError("The query parameter must be a dictionary.")

        try:
            return list(self.collection.find(query))
        except PyMongoError as error:
            print("Read failed: %s" % error)
            return []
