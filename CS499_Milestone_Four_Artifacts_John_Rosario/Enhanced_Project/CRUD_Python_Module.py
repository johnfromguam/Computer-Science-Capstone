import os
from urllib.parse import quote_plus

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError


class AnimalShelter(object):
    """Database access layer for the animal collection in MongoDB."""

    ALLOWED_QUERY_FIELDS = {
        "animal_id",
        "animal_type",
        "breed",
        "color",
        "date_of_birth",
        "datetime",
        "location_lat",
        "location_long",
        "name",
        "outcome_type",
        "rec_num",
        "sex_upon_outcome",
        "age_upon_outcome_in_weeks",
    }
    ALLOWED_OPERATORS = {"$in", "$gte", "$lte", "$gt", "$lt", "$eq", "$ne", "$exists", "$regex"}

    def __init__(
        self,
        username=None,
        password=None,
        host=None,
        port=None,
        database_name=None,
        collection_name=None,
        auth_source=None,
        server_selection_timeout_ms=5000,
    ):
        self.username = username or os.getenv("MONGO_USERNAME")
        self.password = password or os.getenv("MONGO_PASSWORD")
        self.host = host or os.getenv("MONGO_HOST", "localhost")
        self.port = int(port or os.getenv("MONGO_PORT", "27017"))
        self.database_name = database_name or os.getenv("MONGO_DATABASE", "aac")
        self.collection_name = collection_name or os.getenv("MONGO_COLLECTION", "animals")
        self.auth_source = auth_source or os.getenv("MONGO_AUTH_SOURCE", "admin")

        if not self.username or not self.password:
            raise ValueError("MongoDB username and password are required.")

        self.client = MongoClient(
            self._connection_uri(),
            serverSelectionTimeoutMS=server_selection_timeout_ms,
        )
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]

    def _connection_uri(self):
        user = quote_plus(self.username)
        password = quote_plus(self.password)
        return "mongodb://%s:%s@%s:%d/?authSource=%s" % (
            user,
            password,
            self.host,
            self.port,
            quote_plus(self.auth_source),
        )

    def ping(self):
        """Return True when the database connection is reachable."""
        try:
            self.client.admin.command("ping")
            return True
        except PyMongoError as error:
            print("Database ping failed: %s" % error)
            return False

    def create_indexes(self):
        """Create indexes that support the dashboard's most common filters."""
        indexes = [
            [("animal_type", ASCENDING), ("breed", ASCENDING)],
            [("sex_upon_outcome", ASCENDING), ("age_upon_outcome_in_weeks", ASCENDING)],
            [("name", ASCENDING)],
            [("location_lat", ASCENDING), ("location_long", ASCENDING)],
        ]

        created = []
        try:
            for fields in indexes:
                created.append(self.collection.create_index(fields))
        except PyMongoError as error:
            print("Index creation failed: %s" % error)
        return created

    def _validate_query(self, query):
        if query is None:
            return {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")

        for field, value in query.items():
            if field in ("$and", "$or"):
                if not isinstance(value, list):
                    raise ValueError("%s requires a list of query dictionaries." % field)
                for item in value:
                    self._validate_query(item)
                continue

            if field.startswith("$"):
                raise ValueError("Unsupported top-level query operator: %s" % field)
            if field not in self.ALLOWED_QUERY_FIELDS:
                raise ValueError("Unsupported query field: %s" % field)

            if isinstance(value, dict):
                for operator in value:
                    if operator not in self.ALLOWED_OPERATORS:
                        raise ValueError("Unsupported query operator: %s" % operator)

        return query

    def _validate_projection(self, projection):
        if projection is None:
            return None
        if not isinstance(projection, dict):
            raise ValueError("Projection must be a dictionary.")

        for field, included in projection.items():
            if field == "_id":
                continue
            if field not in self.ALLOWED_QUERY_FIELDS:
                raise ValueError("Unsupported projection field: %s" % field)
            if included not in (0, 1, False, True):
                raise ValueError("Projection values must be 0/1 or boolean.")
        return projection

    def create(self, data):
        """Insert one animal record."""
        if not isinstance(data, dict) or not data:
            raise ValueError("Data must be a non-empty dictionary.")
        try:
            result = self.collection.insert_one(data)
            return result.inserted_id is not None
        except PyMongoError as error:
            print("Insert failed: %s" % error)
            return False

    def read(self, query=None, projection=None, limit=0, sort=None):
        """Return records that match a query, projection, limit, and optional sort."""
        query = self._validate_query(query)
        projection = self._validate_projection(projection)
        if limit is None:
            limit = 0
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("Limit must be a non-negative integer.")

        try:
            cursor = self.collection.find(query, projection)
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as error:
            print("Read failed: %s" % error)
            return []

    def update(self, query, update_values, many=False):
        """Update one or many animal records using a controlled $set operation."""
        query = self._validate_query(query)
        if not query:
            raise ValueError("Update requires a non-empty query.")
        if not isinstance(update_values, dict) or not update_values:
            raise ValueError("Update values must be a non-empty dictionary.")

        safe_values = {}
        for field, value in update_values.items():
            if field not in self.ALLOWED_QUERY_FIELDS:
                raise ValueError("Unsupported update field: %s" % field)
            safe_values[field] = value

        try:
            operation = self.collection.update_many if many else self.collection.update_one
            result = operation(query, {"$set": safe_values})
            return result.modified_count
        except PyMongoError as error:
            print("Update failed: %s" % error)
            return 0

    def delete(self, query, many=False):
        """Delete one or many animal records after validating the query."""
        query = self._validate_query(query)
        if not query:
            raise ValueError("Delete requires a non-empty query.")

        try:
            operation = self.collection.delete_many if many else self.collection.delete_one
            result = operation(query)
            return result.deleted_count
        except PyMongoError as error:
            print("Delete failed: %s" % error)
            return 0

    def count(self, query=None):
        """Count records matching a validated query."""
        query = self._validate_query(query)
        try:
            return self.collection.count_documents(query)
        except PyMongoError as error:
            print("Count failed: %s" % error)
            return 0

    def distinct(self, field, query=None):
        """Return distinct values for an allowed field."""
        if field not in self.ALLOWED_QUERY_FIELDS:
            raise ValueError("Unsupported distinct field: %s" % field)
        query = self._validate_query(query)
        try:
            return self.collection.distinct(field, query)
        except PyMongoError as error:
            print("Distinct lookup failed: %s" % error)
            return []
