from pymongo import MongoClient
from pprint import pprint
from datetime import datetime

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['ma_base_de_donnees']
collection = db['utilisateurs']

# Insérer des documents d'exemple
collection.insert_many([
    {
        "nom": "Dupont",
        "interetsActuels": [
            {"url": "https://example.com/sport", "added": "2025-01-01"},
            {"url": "https://example.com/cuisine", "added": "2025-01-02"}
        ],
        "nouveauxInterets": [
            {"url": "https://example.com/lecture", "added": "2025-02-01"},
            {"url": "https://example.com/cuisine", "added": "2025-02-02"}
        ]
    },
    {
        "nom": "Martin",
        "interetsActuels": [
            {"url": "https://example.com/musique", "added": "2025-01-03"}
        ],
        "nouveauxInterets": [
            {"url": "https://example.com/sport", "added": "2025-02-03"},
            {"url": "https://example.com/musique", "added": "2025-02-04"}
        ]
    }
])

# Afficher les documents avant la mise à jour
print("Documents avant la mise à jour:")
for doc in collection.find():
    pprint(doc)

# Effectuer la mise à jour pour fusionner les tableaux
result = collection.update_many(
    {},
    [
        {
            "$set": {
                "interetsActuels": {
                    "$reduce": {
                        "input": {"$concatArrays": ["$interetsActuels", "$nouveauxInterets"]},
                        "initialValue": [],
                        "in": {
                            "$cond": [
                                {"$in": ["$$this.url", "$$value.url"]},
                                "$$value",
                                {"$concatArrays": ["$$value", ["$$this"]]}
                            ]
                        }
                    }
                }
            }
        },
        {
            "$unset": "nouveauxInterets"
        }
    ]
)

print(f"\nNombre de documents mis à jour : {result.modified_count}")

# Afficher les documents après la mise à jour
print("\nDocuments après la mise à jour:")
for doc in collection.find():
    pprint(doc)

# Fermer la connexion
client.close()