import pandas as pd
from pymongo import MongoClient
import json
import os
import time
from datetime import datetime

def safe_json_serialize(obj):
    """Serializa objetos a JSON de forma segura, manejando tipos especiales."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def flatten_doc(doc):
    """Aplana documentos MongoDB con manejo mejorado de tipos anidados."""
    doc = doc.copy()
    doc["id"] = str(doc.pop("_id"))
    
    for k, v in doc.items():
        if isinstance(v, dict):
            doc[k] = json.dumps(v, default=safe_json_serialize, ensure_ascii=False)
        elif isinstance(v, list):
            if k == 'comments' and v and isinstance(v[0], dict):
                simplified = [{
                    'millis': str(c.get('reportMillis', '')),
                    'text': c.get('text', ''),
                    'thumbsUp': str(c.get('isThumbsUp', False))
                } for c in v]
                doc[k] = json.dumps(simplified, ensure_ascii=False)
            else:
                doc[k] = json.dumps(v, default=safe_json_serialize, ensure_ascii=False)
        elif v is None:
            doc[k] = ""
        elif isinstance(v, (int, float, bool)):
            doc[k] = v  # Mantener tipos numéricos
        elif isinstance(v, datetime):
            doc[k] = v.isoformat()
        else:
            doc[k] = str(v).replace('\n', ' ').replace('\r', ' ')
    return doc

# Esperar archivo done.flag
while not os.path.exists("/PROYECTOSD-MAIN/done.flag"):
    print("Esperando que scraper termine...")
    time.sleep(10)

# Conexión Mongo con manejo de errores
try:
    client = MongoClient(
        "mongodb://HM:colocolo123@database:27017/?authSource=admin",
        serverSelectionTimeoutMS=5000
    )
    client.server_info()  # Testear conexión
    db = client['waze']
    collection = db['eventos']

    # Obtener documentos con proyección para excluir campos muy grandes si no son necesarios
    documents = list(collection.find({}, {'imageData': 0, 'rawData': 0}))
    
    if not documents:
        print("La colección está vacía.")
        exit()

    # Procesamiento en lotes para documentos muy grandes
    batch_size = 1000
    flattened_docs = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        flattened_docs.extend([flatten_doc(doc) for doc in batch])

    # Crear DataFrame
    df = pd.DataFrame(flattened_docs)
    
    # Exportar a CSV y Parquet
    csv_path = "/shared/exportado.csv"
    df.to_csv(
        csv_path,
        index=False,
        quoting=1,
        escapechar='\\',
        doublequote=False,
        encoding='utf-8'
    )
    
    parquet_path = "/shared/exportado.parquet"
    df.to_parquet(parquet_path, engine='pyarrow')
    
    print(f"✅ Exportación completada: {csv_path} y {parquet_path}")

except Exception as e:
    print(f"❌ Error durante la exportación: {str(e)}")
    exit(1)
finally:
    client.close()