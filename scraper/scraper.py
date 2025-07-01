import requests
import sys
import os
from pymongo import MongoClient

# Asegurar que storage esté en el path
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))



# Configuración
MONGO_URI = "mongodb://HM:colocolo123@database:27017/waze?authSource=admin"
alertasMinimas = 10000
class MongoStorage:
#    def _init_(self, uri="mongodb+srv://hugomartinez2:colocolo123@cluster0.tbgfql2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="waze", collection_name="eventos"):
    def __init__(self, uri="mongodb://HM:colocolo123@database:27017/waze?authSource=admin",db_name="waze", collection_name="eventos"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_many_events(self, events):
        if events:
            self.collection.insert_many(events)
            print(f"Se insertaron {len(events)} eventos en MongoDB.")
        else:
            print("No hay eventos para insertar.")

def obtener_alertas(b, l, t, r):
    response = requests.get("https://www.waze.com/live-map/api/georss?bottom="+b+"&left="+l+"&top="+t+"&right="+r+"&env=row&types=alerts")
    if response.status_code == 200:
        data = response.json()
        return data.get("alerts", [])  # Lista de alertas
    else:
        print(f"Error al obtener datos: {response.status_code}")
        return []

def main():
    total_alertas = 0
    mongo = MongoStorage(
        uri=MONGO_URI,
        db_name="waze",
        collection_name="eventos"
    )
    
    #coordenadas aproximadas de la region metropolitana
    while (total_alertas < 500):
        for i in range(10):
            for j in range(10): 
                b = str(-33.56672099922156+(i*((33.56672099922156-33.33779053275497)/10)))
                l = str(-70.77841542564796+(j*((70.77841542564796-70.49744008385109)/10)))
                t = str(-33.33779053275497-((10-(i+1))*((33.56672099922156-33.33779053275497)/10)))
                r = str(-70.49744008385109-(((10-j+1))*((70.77841542564796-70.49744008385109)/10)))
                
                # Scraping
                alertas = obtener_alertas(b, l, t, r)

                if not alertas:
                    print(f"No se encontraron alertas para i={i}, j={j}.")
                    continue

                # Guardar en MongoDB
                print(f"hay {len(alertas)} alertas")
                total_alertas += len(alertas)
                print(f"hay {total_alertas} alertas en total")
                mongo.insert_many_events(alertas)
    with open("/PROYECTOSD-MAIN/done.flag", "w") as f:
        f.write("done")

if __name__ == "__main__":
    main()
    