def menu():
    while True:
        print("\n--- MENU ---")
        print("1. Admin")
        print("2. User")

        main_option = input("Selecciona una opción: ")

        if main_option == "1":
            print("\n--- ACCIONES ADMIN ---")
            print("1. Cargar datos")
            print("2. Borrar DB")


            admin_option = input("Selecciona una opción: ")

            if admin_option == "1":
                pass
            elif admin_option == "2":
                pass







        elif main_option == "2":
            print("\n--- ACCIONES USER ---")
            print("1. Consultar datos de mi perfil")
            print("2. Consultar datos de un torneo")
            print("3. Consultar datos de un equipo")
            print("4. Consultar datos de un jugador")
            print("5. Consultar apuestas disponibles")

            user_option = input("Selecciona una opción: ")

            if user_option == "1":
                print("\n--- MENU PERFIL ---")
                print("1. Datos de mi perfil")
                print("2. Historial de apuestas")
                print("3. Historial de transacciones")
                print("4. Mis amigos")


                user_opc = input("Selecciona una opción: ")

                if user_opc == "1":
                    print("\n--- DATOS DE MI PERFIL ---")
                    print("1. Consultar por identificador/email del usuario autenticado (Req. 2 - MongoDB)")
                    print("2. Ranking de jugadores (Regional)")
                    print("3. Mejores usuarios por región (DGraph)")
                    print("4. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        print("AQUI VA LA FUNCION DEL REQUERIMIENTO 2 - MongoDB")
                    elif opt == "2":
                        print(" AQUI VA LA FUNCION PARA MOSTRAR EL RANKING DE JUGADORES")
                    elif opt == "3":
                        region = input("Ingrese la región (América o Europa): ")
                        print("AQUI VA LA FUNCION PARA MOSTRAR LOS MEJORES USUARIOS POR REGION")
                    elif opt == "4":
                        pass

                elif user_opc == "2":
                    print("\n--- HISTORIAL DE APUESTAS ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR EL HISTORIAL DE APUESTAS")
                    print("1. Requerimiento 1 - Historial de apuestas - Cassandra")
                    print("2. Requerimiento 2 - Top 5 apuestas más rentables - Cassandra")
                    print("3. Mis mejores apuestas")
                    print("4. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        nombre_usuario = input("Ingrese el nombre de usuario: ")
                        temporada = input("Ingrese la temporada: ")
                        print("AQUI VA LA FUNCION DEL REQUERIMIENTO 1 - Cassandra")
                    elif opt == "2":
                        nombre_usuario = input("Ingrese el nombre de usuario: ")
                        temporada = input("Ingrese la temporada: ")
                        print("AQUI VA LA FUNCION DEL REQUERIMIENTO 2 - Cassandra")
                    elif opt == "3":
                        print(" AQUI VA LA FUNCION PARA MOSTRAR LAS MEJORES  APUESTAS")
                    elif opt == "4":
                        pass

                elif user_opc == "3":
                    print("\n--- HISTORIAL DE TRANSACCIONES ---")
                    print("1. Requerimiento 8 - Historial de transacciones de un usuario - Cassandra")
                    print("2. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        nombre_usuario = input("Ingrese el nombre de usuario: ")
                        anio_actual = input("Ingrese el año actual: ")
                        print("AQUI VA LA FUNCION DEL REQUERIMIENTO 8 - Cassandra")
                    elif opt == "2":
                        pass

                elif user_opc == "4":
                    print("\n--- MIS AMIGOS ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR LA LISTA DE AMIGOS")
                    print("1. Competencia semanal VS amigo (DGraph)")
                    print("2. Apuestas más populares del amigo por categoría (DGraph)")
                    print("3. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        amigo = input("Ingrese el nombre del amigo: ")
                        semana = input("Ingrese la semana (1-52): ")
                        print("AQUI VA LA FUNCION PARA MOSTRAR APUESTAS GANADAS/PERDIDAS, PORCENTAJES Y GANADOR SEMANAL")
                    elif opt == "2":
                        amigo = input("Ingrese el nombre del amigo: ")
                        categoria = input("Ingrese la categoría (Jugador, Equipo o Torneo): ")
                        print("AQUI VA LA FUNCION PARA MOSTRAR LAS APUESTAS MAS POPULARES DEL AMIGO POR CATEGORIA")
                    elif opt == "3":
                        pass

            elif user_option == "2":
                print("\n--- TORNEOS DISPONIBLES ---")
                print(" AQUI VA LA FUNCION PARA MOSTRAR LOS TORNEOS DISPONIBLES")
                torneo = input("Ingrese el nombre del torneo: ")

                print("\n--- MENU TORNEO ---")
                print("1. Req. 4 - MongoDB - Consulta por nombre del torneo")
                print("2. Req. 8 - MongoDB - Consulta por nombre del torneo")
                print("3. Requerimiento 3 - Top 5 goleadores por torneo - Cassandra")
                print("4. Requerimiento 4 - Porteros más goleados del torneo - Cassandra")
                print("5. Requerimiento 5 - Historial de partidos de un torneo - Cassandra")
                print("6. Mejores jugadores de la liga (DGraph)")
                print("7. Volver al menu principal")


                option = input("Selecciona una opción: ")

                if option == "1":
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 4 - MongoDB")
                elif option == "2":
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 8 - MongoDB")
                elif option == "3":
                    temporada = input("Ingrese la temporada: ")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 3 - Cassandra")
                elif option == "4":
                    temporada = input("Ingrese la temporada: ")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 4 (PORTEROS MAS GOLEADOS) - Cassandra")
                elif option == "5":
                    temporada = input("Ingrese la temporada: ")
                    jornada = None
                    incluir_jornada = input("¿Desea filtrar por jornada? (s/n): ")
                    if incluir_jornada.lower() == "s":
                        try:
                            jornada = int(input("Ingrese la jornada: "))
                        except ValueError:
                            print("La jornada debe ser un número entero.")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 5 - Cassandra")
                elif option == "6":
                    temporada = input("Ingrese la temporada: ")
                    print("AQUI VA LA FUNCION PARA MOSTRAR LOS MEJORES JUGADORES DE LA LIGA")
                elif option == "7":
                    pass
            
            elif user_option == "3":
                print("\n--- MENU EQUIPO ---")
                print("1. Consultar por nombre del equipo (Req. 7 - MongoDB)")
                print("2. Requerimiento 6 - Historial de tarjetas de un equipo - Cassandra")
                print("3. Requerimiento 7 - Historial de partidos de un equipo - Cassandra")
                print("4. Equipos similares por región (DGraph)")
                print("5. Volver al menu principal")

                team_option = input("Selecciona una opción: ")

                if team_option == "1":
                    nombre_equipo = input("Ingrese el nombre del equipo: ")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 7 - MongoDB")
                elif team_option == "2":
                    nombre_equipo = input("Ingrese el nombre del equipo: ")
                    temporada = input("Ingrese la temporada: ")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 6 - Cassandra")
                elif team_option == "3":
                    nombre_equipo = input("Ingrese el nombre del equipo: ")
                    nombre_torneo = input("Ingrese el nombre del torneo: ")
                    temporada = input("Ingrese la temporada: ")
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 7 (HISTORIAL DE PARTIDOS) - Cassandra")
                elif team_option == "4":
                    nombre_equipo = input("Ingrese el nombre del equipo: ")
                    region = input("Ingrese la región del equipo: ")
                    print("AQUI VA LA FUNCION PARA MOSTRAR 5 EQUIPOS SIMILARES POR REGION")
                elif team_option == "5":
                    pass

            elif user_option == "4":
                print("\n--- MENU JUGADOR ---")
                print("--- CONSULTAS POR NOMBRE DEL JUGADOR ---")
                print("1. Req. 1 - MongoDB")
                print("2. Req. 6 - MongoDB")
                print("3. Apuestas disponibles y jugadores con características similares (DGraph)")
                print("4. Volver al menu principal")

                player_option = input("Selecciona un requerimiento: ")

                if player_option == "1":
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 1 - MongoDB")
                elif player_option == "2":
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 6 - MongoDB")
                elif player_option == "3":
                    nombre_jugador = input("Ingrese el nombre del jugador: ")
                    print("AQUI VA LA FUNCION PARA MOSTRAR SUS APUESTAS Y 5 JUGADORES SIMILARES")
                elif player_option == "4":
                    pass

            elif user_option == "5":
                print("\n--- MENU APUESTAS DISPONIBLES ---")
                print("1. Consultar por Nombre del Equipo A + Nombre del Equipo B (Req. 5 - MongoDB)")
                print("2. Recomendar apuestas por características similares (DGraph)")
                print("3. Recomendar equipos en racha (DGraph)")
                print("4. Volver al menu principal")

                bet_option = input("Selecciona una opción: ")

                if bet_option == "1":
                    print("AQUI VA LA FUNCION DEL REQUERIMIENTO 5 - MongoDB")
                elif bet_option == "2":
                    porcentaje_ganancia = input("Ingrese el porcentaje de ganancia de la apuesta original: ")
                    liga = input("Ingrese la liga de la apuesta original: ")
                    equipo = input("Ingrese el equipo de la apuesta original: ")
                    print("AQUI VA LA FUNCION PARA MOSTRAR 5 APUESTAS SIMILARES POR GANANCIA, LIGA O EQUIPO")
                elif bet_option == "3":
                    print("AQUI VA LA FUNCION PARA MOSTRAR 5 EQUIPOS RECOMENDADOS POR SUS ULTIMOS 10 PARTIDOS")
                elif bet_option == "4":
                    pass
        
        else:
            print("Opción inválida")


def main():
    menu()