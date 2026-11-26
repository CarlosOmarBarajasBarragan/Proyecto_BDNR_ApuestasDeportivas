import falcon
from bson.objectid import ObjectId
from datetime import datetime


class MongoApuestasResource:
    def __init__(self, db):
        self.db = db

    def _serializar(self, data):
        """Convierte ObjectId y datetime a string para evitar errores de serialización en Falcon."""
        if isinstance(data, list):
            return [self._serializar(item) for item in data]
        if isinstance(data, dict):
            return {k: self._serializar(v) for k, v in data.items()}
        if isinstance(data, ObjectId):
            return str(data)
        if isinstance(data, datetime):
            return data.isoformat()
        return data

    def _get_oid_by_field(self, collection, field, value, label):
        """Busca un documento por nombre/email y devuelve su _id."""
        if not value:
            raise falcon.HTTPBadRequest(description=f"Falta el parámetro obligatorio: {label}")
        doc = collection.find_one({field: value}, {"_id": 1})
        if not doc:
            raise falcon.HTTPNotFound(description=f"No se encontró {label}: '{value}'")
        return doc["_id"]

    async def on_get(self, req, resp, req_num):
        # Parámetros legibles enviados por el usuario
        jugador = req.get_param('jugador')
        competicion = req.get_param('competicion')
        usuario = req.get_param('usuario')
        equipo = req.get_param('equipo')
        equipo_b = req.get_param('equipo_b')
        torneo = req.get_param('torneo')
        temporada = req.get_param('temporada')

        resultados = []

        if req_num == "1":
            # Req 1 - Historial de goles de un jugador
            jid = self._get_oid_by_field(self.db.Jugador, "nombre", jugador, "jugador")
            pipeline = [
                {"$match": {"jugador_id": jid, "competicion": competicion}},
                {"$group": {
                    "_id": {
                        "jugador": "$jugador",
                        "competicion": "$competicion",
                        "rival": "$rival",
                        "temporada": "$temporada"
                    },
                    "cantidad_goles": {"$sum": "$goles"}
                }},
                {"$match": {"cantidad_goles": {"$gt": 0}}},
                {"$project": {
                    "_id": 0,
                    "jugador": "$_id.jugador",
                    "competicion": "$_id.competicion",
                    "rival": "$_id.rival",
                    "temporada": "$_id.temporada",
                    "cantidad_goles": 1
                }},
                {"$sort": {"cantidad_goles": -1}},
                {"$group": {
                    "_id": None,
                    "historial": {"$push": "$$ROOT"},
                    "total_goles": {"$sum": "$cantidad_goles"}
                }},
                {"$project": {"_id": 0, "historial": 1, "total_goles": 1}}
            ]
            resultados = list(self.db.Estadisticas_jugador_partido.aggregate(pipeline))

        elif req_num == "2":
            # Req 2 - Resumen del historial de apuestas de un usuario (busca por email o nombre)
            if not usuario:
                raise falcon.HTTPBadRequest(description="Falta el parámetro obligatorio: usuario")
            user_doc = self.db.Usuarios.find_one(
                {"$or": [{"email": usuario}, {"nombre": usuario}]},
                {"_id": 1}
            )
            if not user_doc:
                raise falcon.HTTPNotFound(description=f"No se encontró el usuario: '{usuario}'")
            uid = user_doc["_id"]

            # 1) Listado cronológico
            cursor_lista = self.db.Apuestas.find(
                {"usuario_id": uid},
                {"_id": 0, "monto": 1, "evento": 1, "fecha": 1, "estado": 1}
            ).sort("fecha", -1)
            lista_apuestas = list(cursor_lista)

            # 2) Resumen estadístico agrupado por estado y torneo
            pipeline = [
                {"$match": {"usuario_id": uid}},
                {"$group": {
                    "_id": {"estado": "$estado", "torneo": "$torneo"},
                    "num_apuestas": {"$sum": 1},
                    "total_apostado": {"$sum": "$monto"},
                    "total_ganado": {"$sum": "$ganancia"}
                }},
                {"$setWindowFields": {
                    "partitionBy": "$_id.torneo",
                    "output": {"total_torneo": {"$sum": "$num_apuestas"}}
                }},
                {"$project": {
                    "_id": 0,
                    "estado": "$_id.estado",
                    "torneo": "$_id.torneo",
                    "num_apuestas": 1,
                    "total_apostado": 1,
                    "total_ganado": 1,
                    "porcentaje_acierto": {
                        "$cond": [
                            {"$eq": ["$_id.estado", "Ganada"]},
                            {"$round": [{"$multiply": [{"$divide": ["$num_apuestas", "$total_torneo"]}, 100]}, 2]},
                            0
                        ]
                    }
                }}
            ]
            resumen_apuestas = list(self.db.Apuestas.aggregate(pipeline))

            resultados = {
                "historial": lista_apuestas,
                "resumen": resumen_apuestas
            }

        elif req_num == "3":
            # Req 3 - Rendimiento de un jugador por temporada
            jid = self._get_oid_by_field(self.db.Jugador, "nombre", jugador, "jugador")
            cursor = self.db.Estadisticas_jugador_partido.find(
                {"jugador_id": jid, "temporada": temporada},
                {
                    "_id": 0, "temporada": 1, "fecha_partido": 1, "estado_partido": 1,
                    "minutos_jugados": 1, "goles": 1, "asistencias": 1,
                    "tarjetas_amarillas": 1, "tarjetas_rojas": 1
                }
            ).sort("fecha_partido", 1)
            resultados = list(cursor)

        elif req_num == "4":
            # Req 4 - Los 5 jugadores más jóvenes inscritos por Torneo
            if not torneo:
                raise falcon.HTTPBadRequest(description="Falta el parámetro obligatorio: torneo")

            pipeline = [
                {"$match": {"nombre": torneo}},
                {"$lookup": {
                    "from": "Plantillas",
                    "let": {"id": "$_id", "temp": "$temporada_actual"},
                    "pipeline": [
                        {"$match": {"$expr": {"$and": [
                            {"$eq": ["$torneo_id", "$$id"]},
                            {"$eq": ["$temporada", "$$temp"]}
                        ]}}},
                        {"$sort": {"fecha_nacimiento": -1}},
                        {"$limit": 5}
                    ],
                    "as": "p"
                }},
                {"$unwind": "$p"},
                {"$sort": {"p.fecha_nacimiento": -1}},
                {"$project": {
                    "_id": 0,
                    "temporada": "$p.temporada",
                    "nombre_jugador": "$p.nombre_jugador",
                    "edad": {"$floor": {"$divide": [{"$subtract": ["$$NOW", "$p.fecha_nacimiento"]}, 31557600000]}},
                    "nombre_torneo": "$nombre",
                    "equipo": "$p.equipo",
                    "partidos_jugados": "$p.partidos_jugados"
                }}
            ]
            resultados = list(self.db.Torneo.aggregate(pipeline))

        elif req_num == "5":
            # Req 5 - Balance de enfrentamientos directos entre dos equipos
            A = self._get_oid_by_field(self.db.Equipos, "nombre", equipo, "equipo A")
            B = self._get_oid_by_field(self.db.Equipos, "nombre", equipo_b, "equipo B")

            filtro_enfrentamiento = {
                "estado_partido": "Finalizado",
                "$or": [
                    {"local.equipo_id": A, "visitante.equipo_id": B},
                    {"local.equipo_id": B, "visitante.equipo_id": A}
                ]
            }

            cursor_detalle = self.db.Partidos.find(
                filtro_enfrentamiento,
                {
                    "_id": 0, "fecha_partido": 1, "sede": 1, "competicion": 1,
                    "local.nombre": 1, "local.goles": 1,
                    "visitante.nombre": 1, "visitante.goles": 1
                }
            ).sort("fecha_partido", -1)
            detalle_partidos = list(cursor_detalle)

            pipeline = [
                {"$match": filtro_enfrentamiento},
                {"$addFields": {
                    "golesA": {"$cond": [{"$eq": ["$local.equipo_id", A]}, "$local.goles", "$visitante.goles"]},
                    "golesB": {"$cond": [{"$eq": ["$local.equipo_id", B]}, "$local.goles", "$visitante.goles"]}
                }},
                {"$group": {
                    "_id": None,
                    "total_partidos": {"$sum": 1},
                    "victorias_equipo_a": {"$sum": {"$cond": [{"$gt": ["$golesA", "$golesB"]}, 1, 0]}},
                    "victorias_equipo_b": {"$sum": {"$cond": [{"$gt": ["$golesB", "$golesA"]}, 1, 0]}},
                    "empates": {"$sum": {"$cond": [{"$eq": ["$golesA", "$golesB"]}, 1, 0]}},
                    "promedio_goles": {"$avg": {"$add": ["$golesA", "$golesB"]}}
                }},
                {"$project": {
                    "_id": 0,
                    "total_partidos": 1,
                    "victorias_equipo_a": 1,
                    "victorias_equipo_b": 1,
                    "empates": 1,
                    "promedio_goles": {"$round": ["$promedio_goles", 2]}
                }}
            ]
            resumen_balance = list(self.db.Partidos.aggregate(pipeline))

            resultados = {
                "balance": resumen_balance[0] if resumen_balance else {},
                "partidos": detalle_partidos
            }

        elif req_num == "6":
            # Req 6 - Trayectoria de un jugador
            jid = self._get_oid_by_field(self.db.Jugador, "nombre", jugador, "jugador")
            pipeline = [
                {"$match": {"_id": jid}},
                {"$project": {
                    "_id": 0,
                    "nombre": 1,
                    "trayectoria": {"$sortArray": {"input": "$trayectoria", "sortBy": {"temporada": 1}}}
                }}
            ]
            resultados = list(self.db.Jugador.aggregate(pipeline))

        elif req_num == "7":
            # Req 7 - Resultados de un equipo en el Torneo actual
            E = self._get_oid_by_field(self.db.Equipos, "nombre", equipo, "equipo")
            pipeline = [
                {"$match": {
                    "temporada": temporada,
                    "$or": [{"local.equipo_id": E}, {"visitante.equipo_id": E}]
                }},
                {"$project": {
                    "_id": 0,
                    "temporada": 1,
                    "fecha_partido": 1,
                    "estado_partido": 1,
                    "equipo_rival": {"$cond": [{"$eq": ["$local.equipo_id", E]}, "$visitante.nombre", "$local.nombre"]},
                    "goles_a_favor": {"$cond": [{"$eq": ["$local.equipo_id", E]}, "$local.goles", "$visitante.goles"]},
                    "goles_contra": {"$cond": [{"$eq": ["$local.equipo_id", E]}, "$visitante.goles", "$local.goles"]},
                    "goleadores": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$goles",
                                    "as": "g",
                                    "cond": {"$and": [
                                        {"$eq": ["$$g.equipo_id", E]},
                                        {"$ne": ["$$g.tipo", "autogol"]}
                                    ]}
                                }
                            },
                            "as": "g",
                            "in": "$$g.jugador"
                        }
                    }
                }},
                {"$sort": {"fecha_partido": -1}}
            ]
            resultados = list(self.db.Partidos.aggregate(pipeline))

        elif req_num == "8":
            # Req 8 - Tabla de posiciones (Torneo actual)
            tid = self._get_oid_by_field(self.db.Torneo, "nombre", torneo, "torneo")
            cursor = self.db.Tabla_posiciones.find(
                {"torneo_id": tid, "temporada": temporada},
                {
                    "_id": 0, "temporada": 1, "nombre_equipo": 1, "puntos": 1,
                    "partidos_jugados": 1, "victorias": 1, "empates": 1,
                    "derrotas": 1, "goles_favor": 1, "goles_contra": 1,
                    "diferencia_goles": 1
                }
            ).sort([("puntos", -1), ("diferencia_goles", -1)])
            resultados = list(cursor)

        resp.media = self._serializar(resultados)
        resp.status = falcon.HTTP_200