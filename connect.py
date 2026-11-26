from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from cassandra.cluster import Cluster
import pydgraph


## CONEXION A MONGODB
def get_mongo_db(uri="mongodb://localhost:27017/", db_name="apuestas_db"):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[db_name]
        print("Conectado exitosamente a MongoDB")
        return client, db
    except ConnectionFailure as e:
        print(f"Error conectando a MongoDB: {e}")
        raise e


## CONEXIÓN A CASSANDRA
def get_cassandra_session(hosts=['127.0.0.1'], port=9042):
    try:
        cluster = Cluster(hosts, port=port)
        session = cluster.connect()
        print("Conectado exitosamente a Apache Cassandra")
        return cluster, session
    except Exception as e:
        print(f"Error conectando a Cassandra: {e}")
        raise e


def setup_mongo_indexes(db):
    # Búsquedas por nombre o email
    db.Torneo.create_index([("nombre", 1)], unique=True)
    db.Equipos.create_index([("nombre", 1)])
    db.Usuarios.create_index([("email", 1)], unique=True)
    db.Jugador.create_index([("nombre", 1)])

    # Req. 1 y Req. 3: Estadísticas de jugador por partido
    db.Estadisticas_jugador_partido.create_index([("jugador_id", 1), ("competicion", 1)])
    db.Estadisticas_jugador_partido.create_index([("jugador_id", 1), ("temporada", 1), ("fecha_partido", 1)])

    # Req. 2: Apuestas por usuario (agrupadas por estado/torneo y cronológicas)
    db.Apuestas.create_index([("usuario_id", 1), ("estado", 1), ("torneo", 1)])
    db.Apuestas.create_index([("usuario_id", 1), ("fecha", -1)])

    # Req. 4: Jugadores más jóvenes por torneo y temporada
    db.Plantillas.create_index([("torneo_id", 1), ("temporada", 1), ("fecha_nacimiento", -1)])

    # Req. 5 y Req. 7: Enfrentamientos directos y resultados de equipo (local/visitante)
    db.Partidos.create_index([("local.equipo_id", 1), ("visitante.equipo_id", 1)])
    db.Partidos.create_index([("local.equipo_id", 1), ("temporada", 1), ("fecha_partido", -1)])
    db.Partidos.create_index([("visitante.equipo_id", 1), ("temporada", 1), ("fecha_partido", -1)])

    # Req. 8: Tabla de posiciones ordenada por puntos
    db.Tabla_posiciones.create_index([("torneo_id", 1), ("temporada", 1), ("puntos", -1)])

    print("Índices de MongoDB verificados/creados correctamente.")


## CONEXIÓN A DGRAPH
def get_dgraph_client(host='localhost:9080'):
    try:
        stub = pydgraph.DgraphClientStub(host)
        client = pydgraph.DgraphClient(stub)
        print("Conectado exitosamente a Dgraph")
        return stub, client
    except Exception as e:
        print(f"Error conectando a Dgraph: {e}")
        raise e