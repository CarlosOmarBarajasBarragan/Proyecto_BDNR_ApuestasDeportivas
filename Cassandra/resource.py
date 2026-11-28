import falcon

from Cassandra.client import consultar_historial_apuestas


class CassandraApuestasResource:
    def __init__(self, session):
        self.session = session

    async def on_get(self, req, resp, req_num):
        if req_num != "1":
            raise falcon.HTTPNotFound(description="Requerimiento de Cassandra no encontrado.")

        usuario = req.get_param("usuario")
        temporada = req.get_param("temporada")
        if not usuario or not temporada:
            raise falcon.HTTPBadRequest(
                description="Se requieren los parámetros usuario y temporada."
            )

        resp.media = consultar_historial_apuestas(self.session, usuario, temporada)
