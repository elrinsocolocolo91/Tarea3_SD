-- Cargar el archivo JSON
datos = LOAD '/shared/datos.json'
  USING JsonLoader('city:chararray, reportRating:int, reportByMunicipalityUser:boolean, confidence:int, type:chararray, street:chararray');

-- Agrupar por si fue reportado por usuario municipal
muni = GROUP datos BY reportByMunicipalityUser;

-- Contar cantidad de reportes por tipo de usuario
totalMuni = FOREACH muni GENERATE 
  group AS tipo_evento,
  COUNT(datos) AS total;

-- Mostrar resultado
DUMP totalMuni;
