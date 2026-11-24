import falcon
from bson.objectid import ObjectId


class MongoApuestasResource:
    def __init__(self, db):
        self.db = db

    async def on_get(self, req, resp, req_num):
        # Extracción de posibles parámetros de filtro en la URL
        jugador_id = req.get_param('jugador_id')
        competicion = req.get_param('competicion')
        usuario_id = req.get_param('usuario_id')
        equipo_id = req.get_param('equipo_id')
        equipo_b_id = req.get_param('equipo_b_id')
        torneo_id = req.get_param('torneo_id')
        temporada = req.get_param('temporada')

        resultados = []

        if req_num == "1":
            # TODO: Req 1 - Historial de goles de un jugador[cite: 4, 14]
            pass
        elif req_num == "2":
            # TODO: Req 2 - Resumen del historial de apuestas de un usuario[cite: 5, 14]
            pass
        elif req_num == "3":
            # TODO: Req 3 - Rendimiento histórico de un equipo por temporada[cite: 5, 14]
            pass
        elif req_num == "4":
            # TODO: Req 4 - Jugadores más jóvenes inscritos por Torneo[cite: 5, 14]
            pass
        elif req_num == "5":
            # TODO: Req 5 - Balance de enfrentamientos directos entre dos equipos[cite: 5, 14]
            pass
        elif req_num == "6":
            # TODO: Req 6 - Trayectoria de un jugador[cite: 5, 14]
            pass
        elif req_num == "7":
            # TODO: Req 7 - Resultados de un equipo en el Torneo actual[cite: 6, 14]
            pass
        elif req_num == "8":
            # TODO: Req 8 - Tabla de posiciones (Torneo actual)[cite: 6]
            pass

        resp.media = resultados
        resp.status = falcon.HTTP_200