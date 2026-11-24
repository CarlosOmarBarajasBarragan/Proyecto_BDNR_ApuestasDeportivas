import falcon.asgi
import logging
from connect import (
    get_mongo_db,
    get_cassandra_session,
    get_dgraph_client,
    setup_indexes
)
from resources import (
    CassandraResource,
    MongoResource,
    DgraphResource
)
from client import consultar_requerimiento

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoggingMiddleware:
    async def process_request(self, req, resp):
        logger.info(f"Request: {req.method} {req.uri}")

    async def process_response(self, req, resp, resource, req_succeeded):
        logger.info(f"Response: {resp.status} for {req.method} {req.uri}")


# 1. Conexión a las 3 bases de datos
mongo_client, mongo_db = get_mongo_db(uri="mongodb://localhost:27017/", db_name="apuestas_db")
cassandra_cluster, cassandra_session = get_cassandra_session(hosts=['127.0.0.1'], port=9042)
dgraph_stub, dgraph_client = get_dgraph_client(host='localhost:9080')

# 2. Creación/Verificación de índices (MongoDB y Dgraph)
setup_indexes(mongo_db, dgraph_client)

# 3. Inicialización de la aplicación Falcon ASGI
app = falcon.asgi.App(middleware=[LoggingMiddleware()])

# 4. Instancia de recursos (Solo GET) y registro de rutas
cassandra_resource = CassandraResource(cassandra_session)
mongo_resource = MongoResource(mongo_db)
dgraph_resource = DgraphResource(dgraph_client)

app.add_route('/cassandra/req/{req_num}', cassandra_resource)
app.add_route('/mongo/req/{req_num}', mongo_resource)
app.add_route('/dgraph/req/{req_num}', dgraph_resource)


def menu():
    while True:
        print("\n=== MENU PRINCIPAL (APUESTAS DEPORTIVAS) ===")
        print("1. Admin")
        print("2. User")
        print("0. Salir")

        main_option = input("Selecciona una opción: ")

        if main_option == "0":
            print("Cerrando conexiones y saliendo...")
            try:
                mongo_client.close()
                cassandra_cluster.shutdown()
                dgraph_stub.close()
            except Exception as e:
                print(f"Aviso al cerrar conexiones: {e}")
            break
        
        elif main_option == "1":
            print("\n--- ACCIONES ADMIN ---")
            print("1. Cargar datos (Cassandra, MongoDB, Dgraph)")
            print("2. Borrar DB (Cassandra, MongoDB, Dgraph)")
            print("3. Volver al menú principal")

            admin_option = input("Selecciona una opción: ")

            if admin_option == "1":
                # TODO: Llamar al script de ingesta JSON hacia las 3 BDs
                pass
            elif admin_option == "2":
                # TODO: Llamar al script de limpieza de las 3 BDs
                pass

        elif main_option == "2":
            print("\n--- ACCIONES USER ---")
            print("1. Consultar datos de mi perfil")
            print("2. Consultar datos de un torneo")
            print("3. Consultar datos de un equipo")
            print("4. Consultar datos de un jugador")
            print("5. Consultar apuestas disponibles")
            print("6. Volver al menú principal")

            user_option = input("Selecciona una opción: ")

            # 1. PERFIL Y USUARIO
            if user_option == "1":
                print("\n--- MENU PERFIL ---")
                print("1. Datos de mi perfil y rankings")
                print("2. Historial de apuestas")
                print("3. Historial de transacciones")
                print("4. Mis amigos")
                print("5. Volver")

                user_opc = input("Selecciona una opción: ")

                if user_opc == "1":
                    print("\n--- DATOS DE MI PERFIL ---")
                    print("1. Resumen historial de apuestas por estado y liga (Req. 2 - MongoDB)")
                    print("2. Mejores usuarios por región (Req. 4 - Dgraph)")
                    print("3. Volver")

                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        usuario_id = input("Ingrese el usuario_id (ObjectId): ")
                        consultar_requerimiento("mongo", "2", usuario_id=usuario_id)
                    elif opt == "2":
                        region = input("Ingrese la región (América o Europa): ")
                        consultar_requerimiento("dgraph", "4", region=region)

                elif user_opc == "2":
                    print("\n--- HISTORIAL DE APUESTAS ---")
                    print("1. Historial de apuestas de la temporada actual (Req. 1 - Cassandra)")
                    print("2. Top 5 apuestas más rentables de la temporada actual (Req. 2 - Cassandra)")
                    print("3. Volver")

                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        usuario = input("Ingrese el nombre de usuario: ")
                        temporada = input("Ingrese la temporada: ")
                        consultar_requerimiento("cassandra", "1", usuario=usuario, temporada=temporada)
                    elif opt == "2":
                        usuario = input("Ingrese el nombre de usuario: ")
                        temporada = input("Ingrese la temporada: ")
                        consultar_requerimiento("cassandra", "2", usuario=usuario, temporada=temporada)

                elif user_opc == "3":
                    print("\n--- HISTORIAL DE TRANSACCIONES ---")
                    print("1. Historial de transacciones de un usuario (Req. 8 - Cassandra)")
                    print("2. Volver")

                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        usuario = input("Ingrese el nombre de usuario: ")
                        temporada = input("Ingrese el año actual (ej. 2026): ")
                        consultar_requerimiento("cassandra", "8", usuario=usuario, temporada=temporada)

                elif user_opc == "4":
                    print("\n--- MIS AMIGOS ---")
                    print("1. Competencia semanal VS amigo (Req. 6 - Dgraph)")
                    print("2. Apuestas más populares del amigo por categoría (Req. 8 - Dgraph)")
                    print("3. Volver")

                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        usuario = input("Ingrese tu nombre de usuario: ")
                        amigo = input("Ingrese el nombre del amigo: ")
                        semana = input("Ingrese la semana (1-52): ")
                        consultar_requerimiento("dgraph", "6", usuario=usuario, amigo=amigo, semana=semana)
                    elif opt == "2":
                        amigo = input("Ingrese el username del amigo: ")
                        categoria = input("Ingrese la categoría (Jugador, Equipo o Torneo): ")
                        consultar_requerimiento("dgraph", "8", amigo=amigo, categoria=categoria)

            # 2. TORNEOS
            elif user_option == "2":
                print("\n--- MENU TORNEO ---")
                print("1. Jugadores más jóvenes inscritos por Torneo (Req. 4 - MongoDB)")
                print("2. Tabla de posiciones del Torneo actual (Req. 8 - MongoDB)")
                print("3. Top 5 goleadores por torneo (Req. 3 - Cassandra)")
                print("4. Porteros más goleados del torneo (Req. 4 - Cassandra)")
                print("5. Historial de partidos de un torneo (Req. 5 - Cassandra)")
                print("6. Mejores jugadores de cada liga (Req. 7 - Dgraph)")
                print("7. Volver")

                option = input("Selecciona una opción: ")

                if option == "1":
                    torneo_id = input("Ingrese el torneo_id (ObjectId): ")
                    temporada = input("Ingrese la temporada actual: ")
                    consultar_requerimiento("mongo", "4", torneo_id=torneo_id, temporada=temporada)
                elif option == "2":
                    torneo_id = input("Ingrese el torneo_id (ObjectId): ")
                    temporada = input("Ingrese la temporada actual: ")
                    consultar_requerimiento("mongo", "8", torneo_id=torneo_id, temporada=temporada)
                elif option == "3":
                    torneo = input("Ingrese el nombre del torneo: ")
                    temporada = input("Ingrese la temporada: ")
                    consultar_requerimiento("cassandra", "3", torneo=torneo, temporada=temporada)
                elif option == "4":
                    torneo = input("Ingrese el nombre del torneo: ")
                    temporada = input("Ingrese la temporada: ")
                    consultar_requerimiento("cassandra", "4", torneo=torneo, temporada=temporada)
                elif option == "5":
                    torneo = input("Ingrese el nombre del torneo: ")
                    temporada = input("Ingrese la temporada: ")
                    jornada = None
                    incluir_jornada = input("¿Desea filtrar por jornada? (s/n): ")
                    if incluir_jornada.lower() == "s":
                        try:
                            jornada = int(input("Ingrese la jornada: "))
                        except ValueError:
                            print("La jornada debe ser un número entero.")
                    consultar_requerimiento("cassandra", "5", torneo=torneo, temporada=temporada, jornada=jornada)
                elif option == "6":
                    liga = input("Ingrese el nombre de la liga/torneo: ")
                    consultar_requerimiento("dgraph", "7", liga=liga)

            # 3. EQUIPOS
            elif user_option == "3":
                print("\n--- MENU EQUIPO ---")
                print("1. Rendimiento histórico por temporada (Req. 3 - MongoDB)")
                print("2. Resultados y goleadores en el Torneo actual (Req. 7 - MongoDB)")
                print("3. Historial de tarjetas amarillas y rojas (Req. 6 - Cassandra)")
                print("4. Historial de partidos recientes en torneo (Req. 7 - Cassandra)")
                print("5. Recomendación de equipos similares por región (Req. 3 - Dgraph)")
                print("6. Volver")

                team_option = input("Selecciona una opción: ")

                if team_option == "1":
                    equipo_id = input("Ingrese el equipo_id (ObjectId): ")
                    consultar_requerimiento("mongo", "3", equipo_id=equipo_id)
                elif team_option == "2":
                    equipo_id = input("Ingrese el equipo_id (ObjectId): ")
                    temporada = input("Ingrese la temporada actual: ")
                    consultar_requerimiento("mongo", "7", equipo_id=equipo_id, temporada=temporada)
                elif team_option == "3":
                    equipo = input("Ingrese el nombre del equipo: ")
                    temporada = input("Ingrese la temporada: ")
                    consultar_requerimiento("cassandra", "6", equipo=equipo, temporada=temporada)
                elif team_option == "4":
                    equipo = input("Ingrese el nombre del equipo: ")
                    torneo = input("Ingrese el nombre del torneo: ")
                    temporada = input("Ingrese la temporada: ")
                    consultar_requerimiento("cassandra", "7", equipo=equipo, torneo=torneo, temporada=temporada)
                elif team_option == "5":
                    equipo = input("Ingrese el nombre del equipo: ")
                    region = input("Ingrese la región del equipo: ")
                    consultar_requerimiento("dgraph", "3", equipo=equipo, region=region)

            # 4. JUGADORES
            elif user_option == "4":
                print("\n--- MENU JUGADOR ---")
                print("1. Historial de goles por competición y rival (Req. 1 - MongoDB)")
                print("2. Trayectoria completa del jugador (Req. 6 - MongoDB)")
                print("3. Apuestas disponibles y jugadores similares (Req. 1 - Dgraph)")
                print("4. Volver")

                player_option = input("Selecciona una opción: ")

                if player_option == "1":
                    jugador_id = input("Ingrese el jugador_id (ObjectId): ")
                    competicion = input("Ingrese el nombre de la competición: ")
                    consultar_requerimiento("mongo", "1", jugador_id=jugador_id, competicion=competicion)
                elif player_option == "2":
                    jugador_id = input("Ingrese el jugador_id (ObjectId): ")
                    consultar_requerimiento("mongo", "6", jugador_id=jugador_id)
                elif player_option == "3":
                    jugador = input("Ingrese el nombre del jugador: ")
                    consultar_requerimiento("dgraph", "1", jugador=jugador)

            # 5. APUESTAS Y RECOMENDACIONES
            elif user_option == "5":
                print("\n--- MENU APUESTAS Y RECOMENDACIONES ---")
                print("1. Balance de enfrentamientos directos entre dos equipos (Req. 5 - MongoDB)")
                print("2. Recomendar apuestas por características similares (Req. 2 - Dgraph)")
                print("3. Recomendar equipos en racha - últimos 10 partidos (Req. 5 - Dgraph)")
                print("4. Volver")

                bet_option = input("Selecciona una opción: ")

                if bet_option == "1":
                    equipo_id = input("Ingrese el equipo_id del Equipo A (ObjectId): ")
                    equipo_b_id = input("Ingrese el equipo_id del Equipo B (ObjectId): ")
                    consultar_requerimiento("mongo", "5", equipo_id=equipo_id, equipo_b_id=equipo_b_id)
                elif bet_option == "2":
                    porcentaje_ganancia = input("Ingrese el porcentaje de ganancia (opcional): ")
                    liga = input("Ingrese la liga (opcional): ")
                    equipo = input("Ingrese el equipo (opcional): ")
                    consultar_requerimiento(
                        "dgraph", "2",
                        porcentaje_ganancia=porcentaje_ganancia or None,
                        liga=liga or None,
                        equipo=equipo or None
                    )
                elif bet_option == "3":
                    consultar_requerimiento("dgraph", "5")

        else:
            print("Opción inválida")


def main():
    menu()


if __name__ == "__main__":
    main()