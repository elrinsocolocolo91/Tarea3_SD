# Para la ejecución de docker:

- Ejecutar en la terminal y directorio correspondiente al proyecto: docker-compose up --build
- Verificar el funcionamiento por docker.desktop
- El archivo /PROYECTOSD-MAIN/done.flag causa la ejecuación del scraper
# Modificaciones posibles

- Dentro de docker-compose.yml es posible cambiar las politicas de remoción del cache en environment: de redis-stack
- Tener en cuenta que Consultador iniciará las consultas al momento en que el scraper termine de funcionar
- Dentro de Consultador es posible alterar:
  -La cantidad de consultas realizadas
  -El tiempo que permanece activo el generador de consultas
  -Las repeticiones máximas de las consultas
  -El TTL del cache
