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
        print(f" Error conectando a MongoDB: {e}")
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