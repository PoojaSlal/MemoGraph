from neo4j import GraphDatabase

from app.core.config import settings


driver = GraphDatabase.driver(
    settings.memgraph_uri,
    auth=(
        settings.memgraph_username,
        settings.memgraph_password,
    ),
)


def verify_connection():
    with driver.session() as session:
        result = session.run("RETURN 1 AS result")
        return result.single()["result"]
