from datetime import date

import pandas as pd


KEYSPACE = "apuestas_ks"


def ensure_apuestas_usuario_schema(session, keyspace=KEYSPACE):
    session.execute(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """
    )
    session.set_keyspace(keyspace)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS Apuestas_Usuario (
            name_usuario text,
            temporada text,
            fecha_apuesta date,
            apuesta_id text,
            nombre_apuesta text,
            monto_apostado float,
            resultado_apuesta text,
            ganancia_neta float,
            cuota float,
            PRIMARY KEY ((name_usuario, temporada), fecha_apuesta, apuesta_id)
        ) WITH CLUSTERING ORDER BY (fecha_apuesta DESC, apuesta_id ASC)
        """
    )


def populate_apuestas_usuario(session, data_frame, keyspace=KEYSPACE):
    ensure_apuestas_usuario_schema(session, keyspace)
    statement = session.prepare(
        """
        INSERT INTO Apuestas_Usuario (
            name_usuario, temporada, fecha_apuesta, apuesta_id,
            nombre_apuesta, monto_apostado, resultado_apuesta,
            ganancia_neta, cuota
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )

    apuestas = data_frame[data_frame["tipo_entidad"] == "Apuesta"]
    for _, row in apuestas.iterrows():
        fecha = date.fromisoformat(str(row["fecha"]).strip())
        nombre_apuesta = (
            f"{str(row['evento']).strip()} - {str(row['pronostico']).strip()}"
        )
        session.execute(
            statement,
            (
                str(row["nombre_usuario"]).strip(),
                str(row["temporada"]).strip(),
                fecha,
                str(row["apuesta_id"]).strip(),
                nombre_apuesta,
                float(row["monto_apostado"]),
                str(row["estado_apuesta"]).strip(),
                float(row["ganancia_neta"]),
                float(row["cuota"]),
            ),
        )


def consultar_historial_apuestas(session, usuario, temporada):
    rows = session.execute(
        """
        SELECT nombre_apuesta, temporada, fecha_apuesta, monto_apostado,
               resultado_apuesta, ganancia_neta
        FROM apuestas_ks.Apuestas_Usuario
        WHERE name_usuario = %s AND temporada = %s
        """,
        (usuario, temporada),
    )
    return [
        {
            "nombre_apuesta": row.nombre_apuesta,
            "temporada": row.temporada,
            "fecha_apuesta": str(row.fecha_apuesta),
            "monto_apostado": row.monto_apostado,
            "resultado_apuesta": row.resultado_apuesta,
            "ganancia_neta": row.ganancia_neta,
        }
        for row in rows
    ]
