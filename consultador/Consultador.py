import hashlib
import redis
import json
import sys
import random
import asyncio
import os
import time
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from pprint import pprint

while not os.path.exists("/PROYECTOSD-MAIN/done.flag"):
    print("Esperando que scraper termine...")
    time.sleep(1)



class WazeTrafficSimulatorWithCache:
    def __init__(self):
        self.config = {
            'new_query_interval': 1.0,
            'repeat_interval': 5.0,
            'max_repeats': 0,
            'total_unique_queries': 1000,
            'mongo_uri': "mongodb://HM:colocolo123@database:27017/waze?authSource=admin",
            'db_name': "waze",
            'collection_name': "eventos",
            'display_results': True,
            'cache_ttl': 30
        }
        
        try:
            self.mongo_client = MongoClient(self.config['mongo_uri'], serverSelectionTimeoutMS=5000)
            self.mongo_db = self.mongo_client[self.config['db_name']]
            self.collection = self.mongo_db[self.config['collection_name']]
            
            # Verificar conexión a MongoDB
            self.mongo_client.server_info()
            print("✓ Conexión a MongoDB establecida")
            
            # Conexión a Redis con manejo de errores
            self.redis_client = redis.Redis(
                host="redis-stack",
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            print("✓ Conexión a Redis establecida")
            
        except Exception as e:
            print(f"Error de conexión: {str(e)}")
            sys.exit(1)
        
        self.available_ids = self.get_available_ids()
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'query_types': {'by_id': {'count': 0, 'avg_time': 0, 'cache_hits': 0}},
            'last_results': None
        }

    def get_available_ids(self):
        try:
            ids = [str(doc['_id']) for doc in self.collection.find({}, {'_id': 1}).limit(10000)]
            print(f"\nIDs disponibles: {len(ids)}")
            return ids
        except Exception as e:
            print(f"\nError al obtener IDs: {str(e)}")
            return []

    def get_hash_key(self, search_criteria):
        """Genera clave consistente incluyendo el tipo de consulta"""
        if '_id' in search_criteria:
            search_criteria = {'_id': str(search_criteria['_id'])}
        return f"waze:doc:{hashlib.sha256(json.dumps(search_criteria, sort_keys=True).encode()).hexdigest()[:16]}"

    async def execute_query_with_cache(self, query_id, is_repeat=False, forced_id=None):
        """Versión optimizada con mejor manejo de errores"""
        start_time = datetime.now()
        
        if not self.available_ids:
            print("No hay IDs disponibles")
            return None

        try:
            random_id_str = forced_id if forced_id else random.choice(self.available_ids)
            query = {"_id": ObjectId(random_id_str)}
            key = self.get_hash_key(query)
            
            # 1. Intento de obtener de caché
            try:
                cached_value = self.redis_client.get(key)
                if cached_value:
                    self.stats['cache_hits'] += 1
                    self.stats['query_types']['by_id']['cache_hits'] += 1
                    elapsed = (datetime.now() - start_time).total_seconds()
                    
                    if self.config['display_results']:
                        print(f"\n=== CACHE HIT - Consulta {query_id} ===")
                        print(f"Clave: {key} | Duración: {elapsed:.4f}s")
                    
                    return json.loads(cached_value)
            except redis.RedisError as e:
                print(f"Error Redis (get): {str(e)}")

            # 2. Consulta a MongoDB si no hay caché
            self.stats['cache_misses'] += 1
            result = list(self.collection.find(query, {"_id": 1, "type": 1, "subtype": 1}).limit(1))
            
            if result:
                # Convertir ObjectId y preparar para caché
                result[0]['_id'] = str(result[0]['_id'])
                json_result = json.dumps(result)
                
                # Almacenar en caché con manejo de errores
                try:
                    self.redis_client.set(key, json_result, ex=self.config['cache_ttl'])
                    print(f"Documento almacenado en caché: {key}")
                except redis.RedisError as e:
                    print(f"Error Redis (set): {str(e)}")

            # Actualizar estadísticas y mostrar resultados
            elapsed = (datetime.now() - start_time).total_seconds()
            self.stats['total_queries'] += 1
            self.stats['query_types']['by_id']['count'] += 1
            
            if self.config['display_results']:
                status = "HIT" if cached_value else "MISS"
                print(f"\n=== CACHE {status} - Consulta {query_id} ===")
                print(f"ID: {random_id_str} | Clave: {key}")
                print(f"Duración: {elapsed:.2f}s | Docs: {len(result)}")
            
            return result if result else None

        except Exception as e:
            print(f"\nError en query {query_id}: {str(e)}")
            return None

    def determine_repeats(self):
        rand = random.random()
        if rand < 0.3: return 0
        elif rand < 0.7: return random.randint(1, 2)
        return self.config['max_repeats']

    async def schedule_repeats(self, query_id, original_id):
        repeats = self.determine_repeats()
        if repeats == 0:
            print(f"\nConsulta {query_id} no tendrá repeticiones")
            return
            
        for repeat_num in range(1, repeats + 1):
            await asyncio.sleep(self.config['repeat_interval'])
            print(f"\n[REPETICIÓN {repeat_num}/{repeats} - Consulta {query_id}]")
            await self.execute_query_with_cache(query_id, is_repeat=True, forced_id=original_id)

    async def generate_queries(self):
        """Versión corregida con bucle while correctamente indentado"""
        query_id = 0
        
        while query_id < self.config['total_unique_queries']:
            query_id += 1
            original_id = random.choice(self.available_ids)
            
            print(f"\n[NUEVA CONSULTA {query_id} (ID: {original_id})]")
            asyncio.create_task(self.execute_query_with_cache(query_id, forced_id=original_id))
            asyncio.create_task(self.schedule_repeats(query_id, original_id))
            
            await asyncio.sleep(self.config['new_query_interval'])

    async def run_simulation(self, duration_minutes=5):
        print("\n=== INICIANDO SIMULACIÓN ===")
        print(f"Duración: {duration_minutes} minutos")
        print(f"Consultas únicas: {self.config['total_unique_queries']}")
        print(f"TTL caché: {self.config['cache_ttl']} segundos")
        
        try:
            await asyncio.wait_for(self.generate_queries(), timeout=duration_minutes*60)
        except asyncio.TimeoutError:
            print("\nTiempo de simulación completado")
        finally:
            self.print_final_stats()

    def print_final_stats(self):
        print("\n" + "="*50)
        print("ESTADÍSTICAS FINALES")
        print(f"Total consultas: {self.stats['total_queries']}")
        print(f"Cache hits: {self.stats['cache_hits']}")
        print(f"Cache misses: {self.stats['cache_misses']}")
        
        if self.stats['total_queries'] > 0:
            hit_rate = (self.stats['cache_hits'] / (self.stats['cache_hits']+ self.stats['cache_misses'])) * 100
            print(f"Tasa de aciertos: {hit_rate:.2f}%")

if __name__ == "__main__":
    simulator = WazeTrafficSimulatorWithCache()
    
    try:
        asyncio.run(simulator.run_simulation(duration_minutes=2))
    except KeyboardInterrupt:
        print("\nSimulación detenida manualmente")
        simulator.print_final_stats()
    except Exception as e:
        print(f"\nError crítico: {str(e)}")