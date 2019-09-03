from pymongo import MongoClient, UpdateOne
from pymongo.errors import InvalidOperation
from bson import ObjectId
import dateutil.parser as parser

"""
Ticket: Migration

Update all the documents in the `movies` collection, such that the "lastupdated"
field is stored as an ISODate() rather than a string.

The parser.parse() method can transform date strings into ISODate objects for
us. We just need to make sure the correct operations are sent to MongoDB!
"""

# ensure you update your host information below!
host = "placeholder"

# don't update this information
MFLIX_DB_NAME = "sample_mflix"
mflix = MongoClient(host)[MFLIX_DB_NAME]

predicate = {"lastupdated": {"$exists": True, "$type": "string"}}
projection = {"lastupdated": 1, "_id": 1}

cursor = mflix.movies.find(predicate, projection)

# this will transform the "lastupdated" field to an ISODate() from a string
movies_to_migrate = []
for doc in cursor:
    doc_id = doc.get('_id')
    lastupdated = doc.get('lastupdated', None)
    movies_to_migrate.append(
        {
            "doc_id": ObjectId(doc_id),
            "lastupdated": parser.parse(lastupdated)
        }
    )

print(f"{len(movies_to_migrate)} documents to migrate")

try:
    bulk_updates = [UpdateOne(
        {"_id": movie.get("doc_id")},
        {"$set": {"lastupdated": movie.get("lastupdated")}}
    ) for movie in movies_to_migrate]

    bulk_results = mflix.movies.bulk_write(bulk_updates)
    print(f"{bulk_results.modified_count} documents updated")

except InvalidOperation:
    print("no updates necessary")
except Exception as e:
    print(str(e))
