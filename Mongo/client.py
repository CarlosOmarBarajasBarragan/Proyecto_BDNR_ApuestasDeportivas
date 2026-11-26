import requests

API_URL = "http://localhost:8000"


def print_resultado(data):
    if not data:
        print("No se encontraron resultados.")
        return

    if isinstance(data, list):
        for doc in data:
            for k, v in doc.items():
                print(f"{k}: {v}")
            print("=" * 50)
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"\n--- {k.upper()} ---")
            if isinstance(v, list):
                print_resultado(v)
            elif isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    print(f"  {sub_k}: {sub_v}")
            else:
                print(f"  {v}")
        print("=" * 50)


def consultar_requerimiento(db_type, req_num, **params):
    url = f"{API_URL}/{db_type}/req/{req_num}"
    query_params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.get(url, params=query_params)
        if response.status_code == 200:
            print_resultado(response.json())
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar con la API. Asegúrate de que uvicorn esté corriendo.")