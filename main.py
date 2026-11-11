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
                    print(" AQUI VA LA FUNCION PARA MOSTRAR LOS DATOS DEL PERFIL")
                    print("1. Ranking de jugadores (Regional)")
                    print("2. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        print(" AQUI VA LA FUNCION PARA MOSTRAR EL RANKING DE JUGADORES")
                    elif opt == "2":
                        pass

                elif user_opc == "2":
                    print("\n--- HISTORIAL DE APUESTAS ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR EL HISTORIAL DE APUESTAS")
                    print("1. Mis mejores apuestas")
                    print("2. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        print(" AQUI VA LA FUNCION PARA MOSTRAR LAS MEJORES  APUESTAS")
                    elif opt == "2":
                        pass

                elif user_opc == "3":
                    print("\n--- HISTORIAL DE TRANSACCIONES ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR EL HISTORIAL DE TRANSACCIONES")
                    print("1. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        pass

                elif user_opc == "4":
                    print("\n--- MIS AMIGOS ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR LA LISTA DE AMIGOS")
                    print("1. Competencia semanal vs amigo")
                    print("2. Apuestas populares entre amigos")
                    print("3. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        amigo = input("Ingrese el nombre del amigo: ")
                        semana = input("Ingrese la semana (1-52): ")
                        print(" AQUI VA LA FUNCION PARA MOSTRAR LA COMPETENCIA SEMANAL VS AMIGO")
                    elif opt == "2":
                        amigo = input("Ingrese el nombre del amigo: ")
                        print(" AQUI VA LA FUNCION PARA MOSTRAR LAS APUESTAS POPULARES ENTRE AMIGOS")
                    elif opt == "3":
                        pass

            elif user_option == "2":
                print("\n--- TORNEOS DISPONIBLES ---")
                print(" AQUI VA LA FUNCION PARA MOSTRAR LOS TORNEOS DISPONIBLES")
                torneo = input("Ingrese el nombre del torneo: ")

                print("\n--- MENU TORNEO ---")
                print("1. Datos de un torneo")
                print("2. Volver al menu principal")


                option = input("Selecciona una opción: ")

                if option == "1":
                    print("\n--- DATOS DE UN TORNEO ---")
                    print(" AQUI VA LA FUNCION PARA MOSTRAR LOS DATOS DEL TORNEO")
                    print("1. Volver al menu principal")


                    opt = input("Selecciona una opción: ")

                    if opt == "1":
                        pass
            
            elif user_option == "3":
                pass
            elif user_option == "4":
                pass
            elif user_option == "5":
                pass
        
        else:
            print("Opción inválida")


def main():
    menu()