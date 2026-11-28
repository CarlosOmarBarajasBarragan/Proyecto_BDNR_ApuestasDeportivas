import csv
import json
import pydgraph

# ------------------------
# CONNECTION
# ------------------------
# Conexión a Dgraph (localhost:9080)
client_stub = pydgraph.DgraphClientStub('localhost:9080')
client = pydgraph.DgraphClient(client_stub)

# ------------------------
# SCHEMA
# ------------------------
def create_schema():
    schema = """

    user.nombre: string @index(hash) .
    email: string @index(hash) .
    fecha_registro: datetime .
    saldo: float .
    porcentaje_victorias: float @index(float) .
    es_amigo_de: [uid] @reverse .
    registra_una: [uid] .

    pais: string @index(hash) .
    continente: string @index(hash) .
    capital: string .

    id_apuesta: string @index(hash) .
    usuario: uid .
    partido: uid @reverse .
    torneo: uid @reverse .
    tipo_apuesta: string .
    categoria: string @index(term) .
    seleccion: string @index(hash) .
    cuota: float .
    monto: float .
    ganancia: float .
    porcentaje_ganancia: float @index(float) .
    apuesta.fecha: datetime .
    semana: int @index(int) .
    estado: string @index(hash) .
    utiliza_una: uid .

    jugador.nombre: string @index(hash) .
    posicion: string @index(fulltext) .
    edad: int .
    pertenece_a: uid @reverse .
    jugador_genera: uid .

    equipo.nombre: string @index(hash) .
    juega_en_un: [uid] @reverse .
    equipo_genera: uid .

    torneo.nombre: string @index(hash) .
    torneo_genera: uid .

    id_partido: string @index(hash) .
    partido.fecha: datetime .
    se_disputa_en_un: uid @reverse .
    partido_genera: uid .

    dt.nombre: string .
    dirige_a: uid .
    dt_genera: uid .

    goles: int @index(int) .
    asistencias: int @index(int) .
    atajadas: int @index(int) .
    victorias: int @index(int) .
    derrotas: int @index(int) .
    goles_anotados: int .
    goles_recibidos: int .
    partidos_racha_positiva: int @index(int) .

    proviene_de: uid @reverse .

    type User {
        user.nombre
        email
        fecha_registro
        saldo
        porcentaje_victorias
        es_amigo_de
        proviene_de
        registra_una
    }

    type LugarOrigen {
        pais
        continente
        capital
    }

    type Apuesta {
        id_apuesta
        usuario
        partido
        torneo
        tipo_apuesta
        categoria
        seleccion
        cuota
        monto
        ganancia
        porcentaje_ganancia
        apuesta.fecha
        semana
        estado
        utiliza_una
    }

    type Jugador {
        jugador.nombre
        posicion
        edad
        pertenece_a
        proviene_de
        jugador_genera
    }

    type Equipo {
        equipo.nombre
        proviene_de
        juega_en_un
        equipo_genera
    }

    type Torneo {
        torneo.nombre
        proviene_de
        torneo_genera
    }

    type Partido {
        id_partido
        partido.fecha
        se_disputa_en_un
        partido_genera
    }

    type DT {
        dt.nombre
        proviene_de
        dirige_a
        dt_genera
    }

    type Estadisticas {
        goles
        asistencias
        atajadas
        victorias
        derrotas
        goles_anotados
        goles_recibidos
        partidos_racha_positiva
    }

    """
    client.alter(pydgraph.Operation(schema=schema))
    print("Schema creado exitosamente.")

# ------------------------
# DROP ALL
# ------------------------
def drop_all():
    confirm = input("Esto eliminará TODO el grafo. ¿Continuar? (s/n): ")

    if confirm.lower() == "s":
        client.alter(pydgraph.Operation(drop_all=True))
        print("Schema y datos eliminados completamente")
    else:
        print("Operación cancelada")


def query_jugador_y_similares(client, nombre_jugador: str, posicion: str):
    query = """
    query q($nombre_jugador: string, $posicion: string) {
        var(func: eq(nombre, $nombre_jugador)) @filter(has(posicion)) {
            JUGADOR_BASE as uid
        }

        jugador_seleccionado(func: uid(JUGADOR_BASE)) {
            nombre
            posicion
            edad
            pertenece_a {
                equipo: nombre
                juega_en_un {
                    liga: nombre
                }
            }
            jugador_genera {
                goles
                asistencias
                atajadas
            }
        }

        apuestas_disponibles(func: eq(seleccion, $nombre_jugador)) {
            Id_apuesta
            tipo_apuesta
            categoria
            seleccion
            cuota
            estado
            partido {
                id_partido
                fecha
            }
            torneo {
                liga: nombre
            }
        }

        jugadores_similares(func: alloftext(posicion, $posicion), first: 5) @filter(NOT uid(JUGADOR_BASE)) {
            nombre
            posicion
            jugador_genera {
                goles
                asistencias
                atajadas
            }
            pertenece_a {
                equipo: nombre
                juega_en_un {
                    liga: nombre
                }
            }
        }
    }
    """

    variables = {
        '$nombre_jugador': nombre_jugador,
        '$posicion': posicion
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))


def query_apuestas_por_ganancia(client, min_porcentaje_ganancia: float):
    query = """
    query q($min_ganancia: float) {
        apuestas_recomendadas(
            func: ge(porcentaje_ganancia, $min_ganancia),
            orderdesc: porcentaje_ganancia,
            first: 5
        ) {
            Id_apuesta
            tipo_apuesta
            categoria
            seleccion
            cuota
            porcentaje_ganancia
            estado
            
            partido {
                id_partido
                fecha
            }
            
            torneo {
                liga: nombre
                equipos: ~juega_en_un {
                    equipo: nombre
                }
            }
        }
    }
    """

    variables = {
        '$min_ganancia': str(min_porcentaje_ganancia)
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))


def query_equipos_victorias_similares_region(client, nombre_equipo: str):
    query = """
    query q($nombre_equipo: string) {
        var(func: eq(nombre, $nombre_equipo)) @filter(has(equipo_genera)) {
            EQUIPO_BASE as uid
            LUGAR_BASE as proviene_de
            equipo_genera {
                V_BASE as victorias
            }
        }

        var(func: uid(LUGAR_BASE)) {
            ~proviene_de @filter(has(equipo_genera) AND NOT uid(EQUIPO_BASE)) {
                equipo_genera {
                    V_CAND_RAW as victorias
                }
                V_CAND as max(val(V_CAND_RAW))
            }
        }

        equipo_seleccionado(func: uid(EQUIPO_BASE)) {
            nombre
            proviene_de {
                Pais
                Continente
            }
            equipo_genera {
                victorias
                derrotas
                goles_anotados
                goles_recibidos
            }
        }

        apuestas_disponibles(func: eq(seleccion, $nombre_equipo)) {
            Id_apuesta
            tipo_apuesta
            categoria
            seleccion
            cuota
            porcentaje_ganancia
            estado
            partido {
                id_partido
                fecha
            }
            torneo {
                liga: nombre
            }
        }

        equipos_similares(func: uid(LUGAR_BASE)) {
            Pais
            Continente
            equipos: ~proviene_de (first: 5, orderdesc: val(V_CAND))
                @filter(has(equipo_genera) AND NOT uid(EQUIPO_BASE) AND ge(val(V_CAND), val(V_BASE))) {
                
                nombre
                equipo_genera {
                    victorias
                    derrotas
                    goles_anotados
                    goles_recibidos
                }
            }
        }
    }
    """

    variables = {
        '$nombre_equipo': nombre_equipo
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))


def query_ranking_usuarios_continente(client, continente: str):
    query = """
    query q($continente: string) {
        var(func: eq(Continente, $continente)) {
            ~proviene_de @filter(has(porcentaje_victorias)) {
                USUARIOS_CONTINENTE as uid
            }
        }

        ranking_usuarios(func: uid(USUARIOS_CONTINENTE),orderdesc: porcentaje_victorias,first: 10) {
            username: nombre
            porcentaje_victorias
            proviene_de {
                pais: Pais
                continente: Continente
            }
        }
    }
    """

    variables = {
        '$continente': continente
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))
    

def query_equipos_en_racha(client, min_partidos_racha: int):

    query = """
    query q($min_racha: int) {
        var(func: has(equipo_genera)) {
            equipo_genera @filter(ge(partidos_racha_positiva, $min_racha)) {
                RACHA as partidos_racha_positiva
            }
            RACHA_EQUIPO as max(val(RACHA))
            EQUIPOS_FILTRADOS as uid
        }

        equipos_en_racha(
            func: uid(EQUIPOS_FILTRADOS),
            orderdesc: val(RACHA_EQUIPO),
            first: 5
        ) @filter(ge(val(RACHA_EQUIPO), $min_racha)) {
            nombre
            juega_en_un {
                liga: nombre
            }
            equipo_genera {
                partidos_racha_positiva
                victorias
                derrotas
                goles_anotados
                goles_recibidos
            }
        }
    }
    """

    variables = {
        '$min_racha': str(min_partidos_racha)
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2, ensure_ascii=False))


def query_competencia_semanal_amigo(client, nombre_usuario: str, nombre_amigo: str, semana: int):
    query = """
    query q($usuario: string, $amigo: string, $semana: int) {
        var(func: eq(nombre, $usuario)) @filter(has(registra_una)) {
            USER_UID as uid
            es_amigo_de @filter(eq(nombre, $amigo)) {
                AMIGO_UID as uid
            }
        }

        usuario(func: uid(USER_UID)) {
            nombre
            apuestas_semana: registra_una @filter(eq(semana, $semana)) {
                Id_apuesta
                tipo_apuesta
                categoria
                seleccion
                cuota
                monto
                ganancia
                semana
                estado
            }
s
            TOTAL_U as count(registra_una @filter(eq(semana, $semana)))
            GANADAS_U as count(registra_una @filter(eq(semana, $semana) AND eq(estado, "ganada")))
            PERDIDAS_U as count(registra_una @filter(eq(semana, $semana) AND eq(estado, "perdida")))
            
            total_apuestas: val(TOTAL_U)
            apuestas_ganadas: val(GANADAS_U)
            apuestas_perdidas: val(PERDIDAS_U)
            porcentaje_ganado: math(cond(TOTAL_U > 0, (GANADAS_U * 100.0) / TOTAL_U, 0.0))
            porcentaje_perdido: math(cond(TOTAL_U > 0, (PERDIDAS_U * 100.0) / TOTAL_U, 0.0))
        }

        amigo(func: uid(AMIGO_UID)) {
            nombre
            apuestas_semana: registra_una @filter(eq(semana, $semana)) {
                Id_apuesta
                tipo_apuesta
                categoria
                seleccion
                cuota
                monto
                ganancia
                semana
                estado
            }
            
            TOTAL_A as count(registra_una @filter(eq(semana, $semana)))
            GANADAS_A as count(registra_una @filter(eq(semana, $semana) AND eq(estado, "ganada")))
            PERDIDAS_A as count(registra_una @filter(eq(semana, $semana) AND eq(estado, "perdida")))
            
            total_apuestas: val(TOTAL_A)
            apuestas_ganadas: val(GANADAS_A)
            apuestas_perdidas: val(PERDIDAS_A)
            porcentaje_ganado: math(cond(TOTAL_A > 0, (GANADAS_A * 100.0) / TOTAL_A, 0.0))
            porcentaje_perdido: math(cond(TOTAL_A > 0, (PERDIDAS_A * 100.0) / TOTAL_A, 0.0))
        }
    }
    """

    variables = {
        '$usuario': nombre_usuario,
        '$amigo': nombre_amigo,
        '$semana': str(semana)
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))


def query_mejores_jugadores_liga(client, nombre_liga: str):
    query = """
    query q($liga: string) {
        var(func: eq(nombre, $liga)) @filter(has(torneo_genera)) {
            ~juega_en_un {
                ~pertenece_a {
                    JUGADORES_LIGA as uid
                    jugador_genera {
                        G as goles
                        A as asistencias
                    }
                    TOTAL_GA as math(G + A)
                }
            }
        }

        mejores_jugadores(
            func: uid(JUGADORES_LIGA),
            orderdesc: val(TOTAL_GA),
            orderdesc: val(G),
            first: 10
        ) {
            nombre
            posicion
            edad
            equipo: pertenece_a {
                nombre
            }
            estadisticas: jugador_genera {
                goles
                asistencias
                total_contribuciones: val(TOTAL_GA)
            }
        }
    }
    """

    variables = {
        '$liga': nombre_liga
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2))


def query_apuestas_populares_amigo(client, nombre_usuario: str, nombre_amigo: str):
    query = """
    query q($usuario: string, $amigo: string) {
        usuario(func: eq(nombre, $usuario)) @filter(has(registra_una)) {
            nombre
            amigos: es_amigo_de {
                nombre
                porcentaje_victorias
            }
        }

        var(func: eq(nombre, $usuario)) @filter(has(registra_una)) {
            es_amigo_de @filter(eq(nombre, $amigo)) {
                AMIGO_UID as uid
                registra_una {
                    APUESTAS_AMIGO as uid
                }
            }
        }

        categoria_jugador(func: uid(APUESTAS_AMIGO)) @filter(allofterms(categoria, "Jugador")) @groupby(seleccion) {
            total_apuestas: count(uid)
        }

        categoria_equipo(func: uid(APUESTAS_AMIGO)) @filter(allofterms(categoria, "Equipo")) @groupby(seleccion) {
            total_apuestas: count(uid)
        }

        categoria_torneo(func: uid(APUESTAS_AMIGO)) @filter(allofterms(categoria, "Torneo")) @groupby(seleccion) {
            total_apuestas: count(uid)
        }
    }
    """

    variables = {
        '$usuario': nombre_usuario,
        '$amigo': nombre_amigo
    }

    res = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(res.json)

    # Extraer la opción más votada (top 1) de cada grupo devuelto por @groupby
    for cat in ["categoria_jugador", "categoria_equipo", "categoria_torneo"]:
        grupos = data.get("data", {}).get(cat, [])
        if grupos and "@groupby" in grupos[0]:
            items = grupos[0]["@groupby"]
            items_ordenados = sorted(items, key=lambda x: x["total_apuestas"], reverse=True)
            data["data"][cat] = items_ordenados[:1]

    print(json.dumps(data, indent=2))

