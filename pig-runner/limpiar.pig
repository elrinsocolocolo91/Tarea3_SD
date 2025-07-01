-- Registrar las librerías necesarias (rutas dentro del contenedor)
REGISTER '/opt/pig/lib/mongo-hadoop-core-2.0.2.jar';
REGISTER '/opt/pig/lib/mongo-hadoop-pig-2.0.2.jar';
REGISTER '/opt/pig/lib/mongo-java-driver-3.12.0.jar';

--esto aquita paralelismo de lectura
SET mongo.input.split.use_range_queries false

REGISTER '/opt/pig/lib/piggybank-0.17.0.jar';
DEFINE CSVLoader org.apache.pig.piggybank.storage.CSVLoader();

-- Usar el nombre del servicio Docker como host
--%default MONGO_URI 'mongodb://HM:colocolo123@database:27017/waze.eventos?authSource=admin'
--%default MONGO_COLLECTION 'eventos'

-- Cargar datos desde MongoDB
--raw_data = LOAD '$MONGO_URI'
--    USING com.mongodb.hadoop.pig.MongoLoader()
--    AS (    
--        _id:chararray,
--        country:chararray,
--       city:chararray,
--        type:chararray,
--        street:chararray,
--        wazeData:chararray,
--        reportByMunicipality:chararray);
raw_data = LOAD '/shared/exportado.csv'
-- id:chararray,country:chararray,city:chararray,type:chararray,street:chararray,wazeData:chararray,reportRating:int,reportByMunicipalityUser:chararray
  USING CSVLoader(',') 
    AS (
        country: chararray,
        nThumbsUp: chararray,
        reportRating: chararray,
        reportByMunicipalityUser: chararray,
        reliability: chararray,
        type: chararray,
        fromNodeId: chararray,
        uuid: chararray,
        speed: chararray,
        reportMood: chararray,
        subtype: chararray,
        street: chararray,
        additionalInfo: chararray,
        toNodeId: chararray,
        id: chararray,
        nComments: chararray,
        reportBy: chararray,
        inscale: chararray,
        comments: chararray,
        confidence: chararray,
        nearBy: chararray,
        roadType: chararray,
        magvar: chararray,
        wazeData: chararray,
        location: chararray,
        pubMillis: chararray,
        city: chararray,
        reportDescription: chararray,
        provider: chararray,
        providerId: chararray,
        imageUrl: chararray,
        imageId: chararray,
        nImages: chararray
    );

-- 2. Filtrado y procesamiento
clean_data = FILTER raw_data BY 
    id IS NOT NULL AND
    type IS NOT NULL;

-- 3. Selección EXACTA de campos que necesitas (en orden correcto)
final_data = FOREACH clean_data GENERATE
    TRIM(street) AS street,
    id AS id,
    TRIM(type) AS incident_type,
    TRIM(country) AS country,
    wazeData AS waze_data,
    TRIM(city) AS city;

-- 4. Verificación antes de guardar
--DUMP final_data;

-- 5. Almacenamiento
--STORE final_data INTO '/shared/waze_processed_data' USING PigStorage(',');
STORE final_data INTO '/usr/share/logstash/ingest_data/waze' USING PigStorage(',');
