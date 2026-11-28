import os
import pydgraph

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')

def create_client_stub():
    """Crea el stub de conexión gRPC con Dgraph."""
    return pydgraph.DgraphClientStub(DGRAPH_URI)


def create_client(client_stub):
    """Crea el cliente principal para interactuar con Dgraph."""
    return pydgraph.DgraphClient(client_stub)


def close_client_stub(client_stub):
    """Cierra la conexión con Dgraph."""
    client_stub.close()