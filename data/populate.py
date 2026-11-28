import pandas as pd
import json
import uuid
from datetime import datetime
from bson import ObjectId
import pydgraph

from connect import (
    get_mongo_db,
    setup_mongo_indexes,
    get_cassandra_session,
    # get_dgraph_client,
)
from Cassandra.client import populate_apuestas_usuario


def parse_date(val):
    if pd.isna(val) or not str(val).strip():
        return None
    return datetime.strptime(str(val).strip(), "%Y-%m-%d")


def clean_str(val):
    return None if pd.isna(val) else str(val).strip()


def clean_int(val, default=0):
    return default if pd.isna(val) else int(float(val))


def clean_float(val, default=0.0):
    return default if pd.isna(val) else float(val)


# ==============================================================================
# 1. POPULATE CASSANDRA (7 Tablas)
# ==============================================================================
def populate_cassandra(session, df, keyspace="apuestas_ks"):
    populate_apuestas_usuario(session, df, keyspace)

    ddls = [
        """
        CREATE TABLE IF NOT EXISTS Goleadores_Torneo (
            name_torneo text,
            temporada text,
            goles_anotados int,
            nombre_jugador text,
            equipo text,
            partidos_jugados int,
            PRIMARY KEY ((name_torneo, temporada), goles_anotados, nombre_jugador)
        ) WITH CLUSTERING ORDER BY (goles_anotados DESC, nombre_jugador ASC);
        """,
        """
        CREATE TABLE IF NOT EXISTS Porteros_Goleados_Torneo (
            name_torneo text,
            temporada text,
            goles_recibidos int,
            nombre_jugador text,
            equipo text,
            partidos_jugados int,
            porterias_cero int,
            PRIMARY KEY ((name_torneo, temporada), goles_recibidos, nombre_jugador)
        ) WITH CLUSTERING ORDER BY (goles_recibidos DESC, nombre_jugador ASC);
        """,
        """
        CREATE TABLE IF NOT EXISTS Partidos_Torneo (
            name_torneo text,
            temporada text,
            jornada int,
            fecha date,
            equipo_local text,
            equipo_visitante text,
            marcador text,
            estado text,
            PRIMARY KEY ((name_torneo, temporada), jornada, fecha, equipo_local)
        ) WITH CLUSTERING ORDER BY (jornada DESC, fecha DESC, equipo_local ASC);
        """,
        """
        CREATE TABLE IF NOT EXISTS Tarjetas_Equipo (
            name_equipo text,
            temporada text,
            fecha date,
            minuto int,
            name_jugador text,
            partido text,
            tipo_tarjeta text,
            total_amarillas int,
            total_rojas int,
            PRIMARY KEY ((name_equipo, temporada), fecha, minuto)
        ) WITH CLUSTERING ORDER BY (fecha DESC, minuto DESC);
        """,
        """
        CREATE TABLE IF NOT EXISTS Partidos_Equipo (
            name_equipo text,
            name_torneo text,
            temporada text,
            fecha date,
            rival text,
            condicion text,
            marcador text,
            resultado text,
            victorias int,
            empates int,
            derrotas int,
            PRIMARY KEY ((name_equipo, name_torneo, temporada), fecha)
        ) WITH CLUSTERING ORDER BY (fecha DESC);
        """,
        """
        CREATE TABLE IF NOT EXISTS Transacciones_Usuario (
            name_usuario text,
            anio_actual text,
            fecha date,
            id_transaccion timeuuid,
            tipo text,
            monto float,
            metodo_pago text,
            estado text,
            saldo_resultante float,
            PRIMARY KEY ((name_usuario, anio_actual), fecha, id_transaccion)
        ) WITH CLUSTERING ORDER BY (fecha DESC, id_transaccion DESC);
        """
    ]
    for ddl in ddls:
        session.execute(ddl)

    jugadores_df = df[df["tipo_entidad"] == "Jugador"].set_index("jugador_id")
    partidos_df = df[df["tipo_entidad"] == "Partido"].set_index("partido_id")
    stats_df = df[df["tipo_entidad"] == "Estadistica_Jugador_Partido"]

    stmt_gol = session.prepare("""
        INSERT INTO Goleadores_Torneo (name_torneo, temporada, goles_anotados, nombre_jugador, equipo, partidos_jugados)
        VALUES (?, ?, ?, ?, ?, ?)
    """)
    stmt_por = session.prepare("""
        INSERT INTO Porteros_Goleados_Torneo (name_torneo, temporada, goles_recibidos, nombre_jugador, equipo, partidos_jugados, porterias_cero)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)
    for (torneo, temp, j_id, j_nom, eq), grp in stats_df.groupby(
        ["nombre_torneo", "temporada", "jugador_id", "nombre_jugador", "nombre_equipo"]
    ):
        pos = jugadores_df.loc[j_id, "posicion"] if j_id in jugadores_df.index else ""
        pj = int(grp["partidos_jugados"].sum())
        if pos == "Portero":
            session.execute(stmt_por, (
                torneo, temp, int(grp["goles_recibidos"].sum()), j_nom, eq, pj, int(grp["porterias_a_cero"].sum())
            ))
        else:
            session.execute(stmt_gol, (
                torneo, temp, int(grp["goles_anotados"].sum()), j_nom, eq, pj
            ))

    stmt_pt = session.prepare("""
        INSERT INTO Partidos_Torneo (name_torneo, temporada, jornada, fecha, equipo_local, equipo_visitante, marcador, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """)
    for _, r in partidos_df.reset_index().iterrows():
        session.execute(stmt_pt, (
            clean_str(r["nombre_torneo"]),
            clean_str(r["temporada"]),
            clean_int(r["jornada"]),
            clean_str(r["fecha"]),
            clean_str(r["equipo_local"]),
            clean_str(r["equipo_visitante"]),
            clean_str(r["marcador"]),
            clean_str(r["estado_partido"])
        ))

    stmt_tar = session.prepare("""
        INSERT INTO Tarjetas_Equipo (name_equipo, temporada, fecha, minuto, name_jugador, partido, tipo_tarjeta, total_amarillas, total_rojas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    tarjetas_df = stats_df[stats_df["tipo_tarjeta"].isin(["Amarilla", "Roja"])].sort_values(["fecha", "minuto_incidencia"])
    acum_tarjetas = {}
    for _, r in tarjetas_df.iterrows():
        eq = clean_str(r["nombre_equipo"])
        temp = clean_str(r["temporada"])
        acum_tarjetas.setdefault((eq, temp), {"am": 0, "ro": 0})
        acum_tarjetas[(eq, temp)]["am"] += clean_int(r["tarjetas_amarillas"])
        acum_tarjetas[(eq, temp)]["ro"] += clean_int(r["tarjetas_rojas"])
        p_id = clean_str(r["partido_id"])
        evento = partidos_df.loc[p_id, "evento"] if p_id in partidos_df.index else f"{eq} vs {clean_str(r['rival'])}"

        session.execute(stmt_tar, (
            eq, temp, clean_str(r["fecha"]), clean_int(r["minuto_incidencia"]),
            clean_str(r["nombre_jugador"]), evento, clean_str(r["tipo_tarjeta"]),
            acum_tarjetas[(eq, temp)]["am"], acum_tarjetas[(eq, temp)]["ro"]
        ))

    stmt_pe = session.prepare("""
        INSERT INTO Partidos_Equipo (name_equipo, name_torneo, temporada, fecha, rival, condicion, marcador, resultado, victorias, empates, derrotas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    acum_ved = {}
    for _, r in partidos_df.reset_index().sort_values("fecha").iterrows():
        torneo = clean_str(r["nombre_torneo"])
        temp = clean_str(r["temporada"])
        fecha = clean_str(r["fecha"])
        gl, gv = clean_int(r["goles_local"]), clean_int(r["goles_visitante"])

        for cond, eq, riv, gf, gc in [
            ("Local", clean_str(r["equipo_local"]), clean_str(r["equipo_visitante"]), gl, gv),
            ("Visitante", clean_str(r["equipo_visitante"]), clean_str(r["equipo_local"]), gv, gl)
        ]:
            key = (eq, torneo, temp)
            acum_ved.setdefault(key, {"v": 0, "e": 0, "d": 0})
            if gf > gc:
                res = "Victoria"
                acum_ved[key]["v"] += 1
            elif gf < gc:
                res = "Derrota"
                acum_ved[key]["d"] += 1
            else:
                res = "Empate"
                acum_ved[key]["e"] += 1

            session.execute(stmt_pe, (
                eq, torneo, temp, fecha, riv, cond, f"{gf}-{gc}", res,
                acum_ved[key]["v"], acum_ved[key]["e"], acum_ved[key]["d"]
            ))

    stmt_trx = session.prepare("""
        INSERT INTO Transacciones_Usuario (name_usuario, anio_actual, fecha, id_transaccion, tipo, monto, metodo_pago, estado, saldo_resultante)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    for _, r in df[df["tipo_entidad"] == "Transaccion_Financiera"].iterrows():
        session.execute(stmt_trx, (
            clean_str(r["nombre_usuario"]),
            str(clean_int(r["anio_actual"])),
            clean_str(r["fecha"]),
            uuid.UUID(clean_str(r["transaccion_id"])),
            clean_str(r["tipo_transaccion"]),
            clean_float(r["monto_transaccion"]),
            clean_str(r["metodo_pago"]),
            clean_str(r["estado_transaccion"]),
            clean_float(r["saldo_resultante"])
        ))

    print("Cassandra poblado exitosamente (7 tablas).")


# ==============================================================================
# 2. POPULATE MONGODB (9 Colecciones con ObjectIds relacionales)
# ==============================================================================
def populate_mongodb(db, df):
    colecciones = [
        "Torneo", "Equipos", "Jugador", "Plantillas", "Partidos",
        "Estadisticas_jugador_partido", "Tabla_posiciones", "Usuarios", "Apuestas"
    ]
    for col in colecciones:
        db[col].drop()

    id_map = {}
    for code in df["id_entidad"].dropna().unique():
        id_map[code] = ObjectId()

    stats_df = df[df["tipo_entidad"] == "Estadistica_Jugador_Partido"]

    # 1. Torneo
    torneos_docs = []
    for _, r in df[df["tipo_entidad"] == "Torneo"].iterrows():
        torneos_docs.append({
            "_id": id_map[r["torneo_id"]],
            "codigo_csv": clean_str(r["torneo_id"]),
            "nombre": clean_str(r["nombre_torneo"]),
            "pais": clean_str(r["pais"]),
            "temporada_actual": clean_str(r["temporada"])
        })
    if torneos_docs:
        db.Torneo.insert_many(torneos_docs)

    # 2. Equipos
    equipos_docs = []
    for _, r in df[df["tipo_entidad"] == "Equipo"].iterrows():
        equipos_docs.append({
            "_id": id_map[r["equipo_id"]],
            "codigo_csv": clean_str(r["equipo_id"]),
            "nombre": clean_str(r["nombre_equipo"]),
            "pais": clean_str(r["pais"]),
            "estadio": clean_str(r["estadio_sede"]),
            "ciudad": clean_str(r["ciudad"]),
            "fundacion": clean_int(r["anio_fundacion"])
        })
    if equipos_docs:
        db.Equipos.insert_many(equipos_docs)

    # 3. Jugador & 4. Plantillas
    jugadores_docs = []
    plantillas_docs = []
    for _, r in df[df["tipo_entidad"] == "Jugador"].iterrows():
        j_code = clean_str(r["jugador_id"])
        eq_code = clean_str(r["equipo_id"])
        tor_code = clean_str(r["torneo_id"])
        j_stats = stats_df[stats_df["jugador_id"] == j_code]
        pj = int(j_stats["partidos_jugados"].sum())
        goles = int(j_stats["goles_anotados"].sum())
        asist = int(j_stats["asistencias"].sum())

        jugadores_docs.append({
            "_id": id_map[j_code],
            "codigo_csv": j_code,
            "nombre": clean_str(r["nombre_jugador"]),
            "fecha_nacimiento": parse_date(r["fecha_nacimiento"]),
            "nacionalidad": clean_str(r["nacionalidad"]),
            "posicion": clean_str(r["posicion"]),
            "equipo_actual_id": id_map[eq_code],
            "trayectoria": [
                {
                    "equipo_id": id_map[eq_code],
                    "equipo": clean_str(r["nombre_equipo"]),
                    "temporada": clean_str(r["temporada"]),
                    "partidos": pj,
                    "goles": goles,
                    "asistencias": asist
                }
            ]
        })

        plantillas_docs.append({
            "temporada": clean_str(r["temporada"]),
            "torneo_id": id_map[tor_code],
            "nombre_torneo": clean_str(r["nombre_torneo"]),
            "equipo_id": id_map[eq_code],
            "equipo": clean_str(r["nombre_equipo"]),
            "jugador_id": id_map[j_code],
            "nombre_jugador": clean_str(r["nombre_jugador"]),
            "fecha_nacimiento": parse_date(r["fecha_nacimiento"]),
            "dorsal": clean_int(r["dorsal"]),
            "partidos_jugados": pj
        })
    if jugadores_docs:
        db.Jugador.insert_many(jugadores_docs)
    if plantillas_docs:
        db.Plantillas.insert_many(plantillas_docs)

    # 5. Partidos
    partidos_docs = []
    for _, r in df[df["tipo_entidad"] == "Partido"].iterrows():
        p_code = clean_str(r["partido_id"])
        p_goles_rows = stats_df[(stats_df["partido_id"] == p_code) & (stats_df["goles_anotados"] > 0)]
        goles_arr = []
        for _, gr in p_goles_rows.iterrows():
            for _ in range(clean_int(gr["goles_anotados"])):
                goles_arr.append({
                    "jugador_id": id_map[clean_str(gr["jugador_id"])],
                    "jugador": clean_str(gr["nombre_jugador"]),
                    "equipo_id": id_map[clean_str(gr["equipo_id"])],
                    "minuto": clean_int(gr["minuto_incidencia"]),
                    "tipo": "normal"
                })

        partidos_docs.append({
            "_id": id_map[p_code],
            "codigo_csv": p_code,
            "temporada": clean_str(r["temporada"]),
            "torneo_id": id_map[clean_str(r["torneo_id"])],
            "competicion": clean_str(r["nombre_torneo"]),
            "jornada": clean_int(r["jornada"]),
            "fecha_partido": parse_date(r["fecha"]),
            "estado_partido": clean_str(r["estado_partido"]),
            "sede": clean_str(r["estadio_sede"]),
            "local": {
                "equipo_id": id_map[clean_str(r["equipo_local_id"])],
                "nombre": clean_str(r["equipo_local"]),
                "goles": clean_int(r["goles_local"])
            },
            "visitante": {
                "equipo_id": id_map[clean_str(r["equipo_visitante_id"])],
                "nombre": clean_str(r["equipo_visitante"]),
                "goles": clean_int(r["goles_visitante"])
            },
            "goles": goles_arr
        })
    if partidos_docs:
        db.Partidos.insert_many(partidos_docs)

    # 6. Estadisticas_jugador_partido
    est_docs = []
    for _, r in stats_df.iterrows():
        est_docs.append({
            "_id": id_map[clean_str(r["id_entidad"])],
            "jugador_id": id_map[clean_str(r["jugador_id"])],
            "jugador": clean_str(r["nombre_jugador"]),
            "partido_id": id_map[clean_str(r["partido_id"])],
            "equipo_id": id_map[clean_str(r["equipo_id"])],
            "rival_id": id_map[clean_str(r["rival_id"])],
            "rival": clean_str(r["rival"]),
            "torneo_id": id_map[clean_str(r["torneo_id"])],
            "competicion": clean_str(r["nombre_torneo"]),
            "temporada": clean_str(r["temporada"]),
            "fecha_partido": parse_date(r["fecha"]),
            "estado_partido": clean_str(r["estado_partido"]),
            "minutos_jugados": clean_int(r["minutos_jugados"]),
            "goles": clean_int(r["goles_anotados"]),
            "asistencias": clean_int(r["asistencias"]),
            "tarjetas_amarillas": clean_int(r["tarjetas_amarillas"]),
            "tarjetas_rojas": clean_int(r["tarjetas_rojas"])
        })
    if est_docs:
        db.Estadisticas_jugador_partido.insert_many(est_docs)

    # 7. Tabla_posiciones
    pos_docs = []
    for _, r in df[df["tipo_entidad"] == "Tabla_Posiciones"].iterrows():
        pos_docs.append({
            "_id": id_map[clean_str(r["id_entidad"])],
            "temporada": clean_str(r["temporada"]),
            "torneo_id": id_map[clean_str(r["torneo_id"])],
            "nombre_torneo": clean_str(r["nombre_torneo"]),
            "equipo_id": id_map[clean_str(r["equipo_id"])],
            "nombre_equipo": clean_str(r["nombre_equipo"]),
            "puntos": clean_int(r["puntos"]),
            "partidos_jugados": clean_int(r["partidos_jugados"]),
            "victorias": clean_int(r["victorias"]),
            "empates": clean_int(r["empates"]),
            "derrotas": clean_int(r["derrotas"]),
            "goles_favor": clean_int(r["goles_anotados"]),
            "goles_contra": clean_int(r["goles_recibidos"]),
            "diferencia_goles": clean_int(r["diferencia_goles"])
        })
    if pos_docs:
        db.Tabla_posiciones.insert_many(pos_docs)

    # 8. Usuarios
    usr_docs = []
    for _, r in df[df["tipo_entidad"] == "Usuario"].iterrows():
        usr_docs.append({
            "_id": id_map[clean_str(r["usuario_id"])],
            "codigo_csv": clean_str(r["usuario_id"]),
            "nombre": clean_str(r["nombre_usuario"]),
            "email": clean_str(r["email"]),
            "fecha_registro": parse_date(r["fecha_registro"]),
            "saldo": clean_float(r["saldo"])
        })
    if usr_docs:
        db.Usuarios.insert_many(usr_docs)

    # 9. Apuestas
    ap_docs = []
    for _, r in df[df["tipo_entidad"] == "Apuesta"].iterrows():
        ap_docs.append({
            "_id": id_map[clean_str(r["apuesta_id"])],
            "codigo_csv": clean_str(r["apuesta_id"]),
            "usuario_id": id_map[clean_str(r["usuario_id"])],
            "partido_id": id_map[clean_str(r["partido_id"])],
            "evento": clean_str(r["evento"]),
            "torneo": clean_str(r["nombre_torneo"]),
            "tipo_apuesta": clean_str(r["tipo_apuesta"]),
            "pronostico": clean_str(r["pronostico"]),
            "cuota": clean_float(r["cuota"]),
            "monto": clean_float(r["monto_apostado"]),
            "ganancia": clean_float(r["ganancia_neta"]),
            "fecha": parse_date(r["fecha"]),
            "estado": clean_str(r["estado_apuesta"])
        })
    if ap_docs:
        db.Apuestas.insert_many(ap_docs)

    print("MongoDB poblado exitosamente (9 colecciones).")


# ==============================================================================
# 3. POPULATE DGRAPH (Nodos y Aristas con blank nodes _:id)
# ==============================================================================
def populate_dgraph(client, df):
    client.alter(pydgraph.Operation(drop_all=True))

    schema = """
    nombre: string @index(hash) .
    pais: string @index(hash) .
    continente: string @index(hash) .
    region: string @index(hash) .
    email: string .
    fecha_registro: datetime .
    saldo: float .
    porcentaje_victorias: float @index(float) .
    es_amigo_de: [uid] @reverse .
    proviene_de: uid @reverse .
    registra_una: [uid] .

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
    fecha: datetime .
    semana: int @index(int) .
    estado: string @index(hash) .
    utiliza_una: uid .

    posicion: string @index(fulltext) .
    edad: int .
    pertenece_a: uid @reverse .
    jugador_genera: uid .

    juega_en_un: [uid] @reverse .
    equipo_genera: uid .
    torneo_genera: uid .

    id_partido: string @index(hash) .
    se_disputa_en_un: uid @reverse .
    partido_genera: uid .

    goles: int @index(int) .
    asistencias: int @index(int) .
    atajadas: int @index(int) .
    victorias: int @index(int) .
    derrotas: int @index(int) .
    goles_anotados: int .
    goles_recibidos: int .
    porcentaje_racha_positiva: float @index(float) .
    type User {
        nombre
        email
        fecha_registro
        saldo
        porcentaje_victorias
        es_amigo_de
        proviene_de
        registra_una
    }

    type Lugar {
        pais
        continente
        capital
        region
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
        fecha
        semana
        estado
        utiliza_una
    }

    type Jugador {
        nombre
        posicion
        edad
        pertenece_a
        proviene_de
        jugador_genera
    }

    type Equipo {
        nombre
        proviene_de
        juega_en_un
        equipo_genera
    }

    type Torneo {
        nombre
        proviene_de
        torneo_genera
    }

    type Partido {
        id_partido
        fecha
        se_disputa_en_un
        partido_genera
    }

    type DT {
        nombre
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
        porcentaje_racha_positiva
    }
    """
    client.alter(pydgraph.Operation(schema=schema))

    nquads = []
    lugares_creados = set()
    stats_df = df[df["tipo_entidad"] == "Estadistica_Jugador_Partido"]
    tabla_df = df[df["tipo_entidad"] == "Tabla_Posiciones"].set_index("equipo_id")

    def get_lugar_uid(pais, cont, reg):
        key = f"{pais}_{reg}".replace(" ", "_").replace(".", "")
        uid = f"_:lugar_{key}"
        if uid not in lugares_creados:
            lugares_creados.add(uid)
            nquads.append({"uid": uid, "dgraph.type": "Lugar", "pais": pais, "continente": cont, "region": reg})
        return uid

    for _, r in df[df["tipo_entidad"] == "Torneo"].iterrows():
        t_id = clean_str(r["torneo_id"])
        l_uid = get_lugar_uid(clean_str(r["pais"]), clean_str(r["continente"]), clean_str(r["region"]))
        nquads.append({
            "uid": f"_:{t_id}",
            "dgraph.type": "Torneo",
            "nombre": clean_str(r["nombre_torneo"]),
            "proviene_de": {"uid": l_uid}
        })

    for _, r in df[df["tipo_entidad"] == "Equipo"].iterrows():
        e_id = clean_str(r["equipo_id"])
        t_id = clean_str(r["torneo_id"])
        l_uid = get_lugar_uid(clean_str(r["pais"]), clean_str(r["continente"]), clean_str(r["region"]))
        st_uid = f"_:stats_{e_id}"

        if e_id in tabla_df.index:
            tr = tabla_df.loc[e_id]
            pj = clean_int(tr["partidos_jugados"])
            vic = clean_int(tr["victorias"])
            der = clean_int(tr["derrotas"])
            ga = clean_int(tr["goles_anotados"])
            gr = clean_int(tr["goles_recibidos"])
            racha = round((vic / pj) * 100, 2) if pj > 0 else 0.0
        else:
            vic = der = ga = gr = 0
            racha = 0.0

        nquads.append({
            "uid": st_uid,
            "dgraph.type": "Estadisticas",
            "victorias": vic,
            "derrotas": der,
            "goles_anotados": ga,
            "goles_recibidos": gr,
            "porcentaje_racha_positiva": float(racha)
        })
        nquads.append({
            "uid": f"_:{e_id}",
            "dgraph.type": "Equipo",
            "nombre": clean_str(r["nombre_equipo"]),
            "proviene_de": {"uid": l_uid},
            "juega_en_un": [{"uid": f"_:{t_id}"}],
            "equipo_genera": {"uid": st_uid}
        })

    for _, r in df[df["tipo_entidad"] == "Jugador"].iterrows():
        j_id = clean_str(r["jugador_id"])
        e_id = clean_str(r["equipo_id"])
        l_uid = get_lugar_uid(clean_str(r["nacionalidad"]), "N/A", clean_str(r["nacionalidad"]))
        st_uid = f"_:stats_{j_id}"

        j_st = stats_df[stats_df["jugador_id"] == j_id]
        goles = int(j_st["goles_anotados"].sum())
        asist = int(j_st["asistencias"].sum())
        ataj = int(j_st["porterias_a_cero"].sum())

        nquads.append({
            "uid": st_uid,
            "dgraph.type": "Estadisticas",
            "goles": goles,
            "asistencias": asist,
            "atajadas": ataj
        })
        nquads.append({
            "uid": f"_:{j_id}",
            "dgraph.type": "Jugador",
            "nombre": clean_str(r["nombre_jugador"]),
            "posicion": clean_str(r["posicion"]),
            "edad": clean_int(r["edad"]),
            "pertenece_a": {"uid": f"_:{e_id}"},
            "proviene_de": {"uid": l_uid},
            "jugador_genera": {"uid": st_uid}
        })

    for _, r in df[df["tipo_entidad"] == "Partido"].iterrows():
        p_id = clean_str(r["partido_id"])
        t_id = clean_str(r["torneo_id"])
        nquads.append({
            "uid": f"_:{p_id}",
            "dgraph.type": "Partido",
            "id_partido": p_id,
            "fecha": f"{clean_str(r['fecha'])}T00:00:00Z",
            "se_disputa_en_un": {"uid": f"_:{t_id}"}
        })

    apuestas_df = df[df["tipo_entidad"] == "Apuesta"]
    for _, r in df[df["tipo_entidad"] == "Usuario"].iterrows():
        u_id = clean_str(r["usuario_id"])
        l_uid = get_lugar_uid(clean_str(r["pais"]), clean_str(r["continente"]), clean_str(r["region"]))
        amigos_raw = clean_str(r["amigos_ids"])
        amigos_uids = [{"uid": f"_:{a.strip()}"} for a in amigos_raw.split(";")] if amigos_raw else []
        user_aps = [{"uid": f"_:{a}"} for a in apuestas_df[apuestas_df["usuario_id"] == u_id]["apuesta_id"]]

        usr_node = {
            "uid": f"_:{u_id}",
            "dgraph.type": "User",
            "nombre": clean_str(r["nombre_usuario"]),
            "email": clean_str(r["email"]),
            "fecha_registro": f"{clean_str(r['fecha_registro'])}T00:00:00Z",
            "saldo": clean_float(r["saldo"]),
            "porcentaje_victorias": clean_float(r["porcentaje_victorias"]),
            "proviene_de": {"uid": l_uid}
        }
        if amigos_uids:
            usr_node["es_amigo_de"] = amigos_uids
        if user_aps:
            usr_node["registra_una"] = user_aps
        nquads.append(usr_node)

    for _, r in apuestas_df.iterrows():
        a_id = clean_str(r["apuesta_id"])
        u_id = clean_str(r["usuario_id"])
        p_id = clean_str(r["partido_id"])
        t_id = clean_str(r["torneo_id"])
        nquads.append({
            "uid": f"_:{a_id}",
            "dgraph.type": "Apuesta",
            "id_apuesta": a_id,
            "usuario": {"uid": f"_:{u_id}"},
            "partido": {"uid": f"_:{p_id}"},
            "torneo": {"uid": f"_:{t_id}"},
            "tipo_apuesta": clean_str(r["tipo_apuesta"]),
            "categoria": clean_str(r["categoria"]),
            "seleccion": clean_str(r["pronostico"]),
            "cuota": clean_float(r["cuota"]),
            "monto": clean_float(r["monto_apostado"]),
            "ganancia": clean_float(r["ganancia_neta"]),
            "porcentaje_ganancia": clean_float(r["porcentaje_ganancia"]),
            "fecha": f"{clean_str(r['fecha'])}T00:00:00Z",
            "semana": clean_int(r["semana"]),
            "estado": clean_str(r["estado_apuesta"])
        })

    txn = client.txn()
    try:
        txn.mutate(set_obj=nquads, commit_now=True)
        print("Dgraph poblado exitosamente (Nodos y Relaciones).")
    finally:
        txn.discard()


# ==============================================================================
# EJECUCIÓN PRINCIPAL (MongoDB y Cassandra)
# ==============================================================================
def run_populate(csv_path="data/instancias_esquema_unificado.csv"):
    df = pd.read_csv(csv_path)

    mongo_client = None
    cassandra_cluster = None

    try:
        cassandra_cluster, cassandra_session = get_cassandra_session()
        mongo_client, mongo_db = get_mongo_db()
        populate_cassandra(cassandra_session, df)
        populate_mongodb(mongo_db, df)
        setup_mongo_indexes(mongo_db)
        # populate_dgraph(dgraph_client, df)
        print("\n=== CARGA DE CASSANDRA (7 TABLAS) Y MONGODB COMPLETADA ===")
    finally:
        if mongo_client is not None:
            mongo_client.close()
        if cassandra_cluster is not None:
            cassandra_cluster.shutdown()
        # dgraph_stub.close()


if __name__ == "__main__":
    run_populate()