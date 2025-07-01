from elasticsearch import Elasticsearch, helpers
import redis
import json
import os
import time

#try:
#    r = redis.Redis(host='redis-stack', port=6379, decode_responses=True)
#    print("Pinging Redis...")
#    r.ping()
#    print("Conexión exitosa a Redis")
#except Exception as e:
#    print("Error al conectar a Redis:", e)

# Esperar a que logstash termine
logstash_done_flag = "/usr/share/logstash/ingest_data/logstash_completed.log"

print("Esperando que Logstash termine de procesar los archivos...")

while not os.path.exists(logstash_done_flag):
    print("Esperando que Logstash termine de procesar los archivos...")
    time.sleep(5)  # espera 5 segundos antes de volver a revisar

print("Logstash ha terminado. Iniciando carga a Redis.")

# Configuración
es = Elasticsearch("http://localhost:9200", basic_auth=("elastic", "contrasena"), verify_certs=False)
r = redis.Redis(host='redis-stack', port=6379, decode_responses=True)

agg = es.search(
    index="logstash*",
    size=0,
    body={
        "aggs": {
            "top_comunas": {
                "terms": { "field": "city.keyword", "size": 1, "order": {"_count": "desc"} }
            }
        }
    }
)

bucket = agg["aggregations"]["top_comunas"]["buckets"][0]
top_comuna = bucket["key"]
count_comuna = bucket["doc_count"]
print(f"🔝 Comuna: {top_comuna} con {count_comuna} alertas.")

query = {
    "query": {
        "term": { "city.keyword": top_comuna }
    }
}

scroll = helpers.scan(es, index="logstash-*", query=query)

alert_ids = []
for doc in scroll:
    alerta = doc["_source"]
    alerta_id = alerta.get("id")
    if not alerta_id:
        continue  # saltar si no tiene ID

    redis_key = f"alerta:{alerta_id}"
    r.set(redis_key, json.dumps(alerta), ex=3600)
    alert_ids.append(redis_key)

#Guardar índice por comuna
r.delete(f"alertas_comuna:{top_comuna}")  # limpiar si ya existía
r.sadd(f"alertas_comuna:{top_comuna}", *alert_ids)
r.expire(f"alertas_comuna:{top_comuna}", 3600)

#Guardar resumen
r.set("top_comuna", top_comuna)
r.set("top_comuna_alertas", count_comuna)

print(f" Guardadas {len(alert_ids)} alertas individuales y su índice bajo 'alertas_comuna:{top_comuna}'")