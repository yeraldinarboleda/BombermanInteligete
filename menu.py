# Definir la función del menú
def mostrar_menu():
    print("Selecciona el tipo de búsqueda:")
    print("1. Búsqueda no informada")
    print("2. Búsqueda informada")
    search_type_opcion = input("Ingresa el número de opción: ")

    if search_type_opcion == "1":
        search_type = "no-informada"
    elif search_type_opcion == "2":
        search_type = "informada"
    else:
        print("Opción inválida, seleccionando búsqueda no informada por defecto.")
        search_type = "no-informada"

    print("\nSelecciona el algoritmo:")
    if search_type == "no-informada":
        print("1. Anchura")
        print("2. Profundidad")
        print("3. Costo Uniforme")

        algorithm_opcion = input("Ingresa el número de opción: ")

        if algorithm_opcion == "1":
            algorithm = "Anchura"
        elif algorithm_opcion == "2":
            algorithm = "Profundidad"
        elif algorithm_opcion == "3":
            algorithm = "Costo Uniforme"
        else:
            print("Opción inválida, seleccionando Anchura por defecto.")
            algorithm = "Anchura"
    else:
        print("1. Beam Search")
        print("2. Hill climbing")
        print("3. A*")
        
        algorithm_opcion = input("Ingresa el número de opción: ")

        if algorithm_opcion == "1":
            algorithm = "Beam Search"
        elif algorithm_opcion == "2":
            algorithm = "Hill climbing"
        elif algorithm_opcion == "3":
            algorithm = "A*"
        else:
            print("Opción inválida, seleccionando Beam Search por defecto.")
            algorithm = "Beam Search"

    heuristic = None
    if search_type == "informada":
        print("\nSelecciona la heurística:")
        print("1. Manhattan")
        print("2. Euclidiana")
        heuristic_opcion = input("Ingresa el número de opción: ")

        if heuristic_opcion == "1":
            heuristic = "Manhattan"
        elif heuristic_opcion == "2":
            heuristic = "Euclidiana"
        else:
            print("Opción inválida, seleccionando Manhattan por defecto.")
            heuristic = "Manhattan"

    return search_type, algorithm, heuristic

