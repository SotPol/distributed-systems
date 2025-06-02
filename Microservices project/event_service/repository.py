# event_service/repository.py
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra'])  # Кластер Cassandra
session = cluster.connect('analytics')  # keyspace analytics

class EventRepository:
    @staticmethod
    def insert_event(data):
        session.execute(
            "INSERT INTO events (id, payload) VALUES (%s, %s)",
            (data["id"], data["payload"])
        )
