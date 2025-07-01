# Usar imagen base más ligera
FROM openjdk:11-jre-slim

#RUN apt-get update && \
#    apt-get install -y wget && \
#    mkdir -p /pig/lib && \
#    wget https://repo1.maven.org/maven2/org/mongodb/mongo-hadoop/mongo-hadoop-core/2.0.2/mongo-hadoop-core-2.0.2.jar -O /pig/lib/mongo-hadoop-core-2.0.2.jar && \
#    apt-get remove -y wget && \
#    apt-get autoremove -y && \
#    rm -rf /var/lib/apt/lists/*

# 1. Instalar dependencias mínimas
RUN apt-get update && apt-get install -y \
    wget \
    tar \
    openssh-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar Hadoop
RUN wget -q https://archive.apache.org/dist/hadoop/core/hadoop-2.7.7/hadoop-2.7.7.tar.gz && \
    tar -xzf hadoop-2.7.7.tar.gz -C /opt && \
    mv /opt/hadoop-2.7.7 /opt/hadoop && \
    rm hadoop-2.7.7.tar.gz

# 5. Instalar Pig
RUN wget -q https://downloads.apache.org/pig/pig-0.17.0/pig-0.17.0.tar.gz && \
    tar -xzf pig-0.17.0.tar.gz -C /opt && \
    mv /opt/pig-0.17.0 /opt/pig && \
    rm pig-0.17.0.tar.gz

# 2. Instalar mongosh desde el release oficial
RUN wget https://downloads.mongodb.com/compass/mongosh-1.8.0-linux-x64.tgz \
    && tar -xzf mongosh-1.8.0-linux-x64.tgz \
    && mv mongosh-1.8.0-linux-x64/bin/mongosh /usr/local/bin/ \
    && rm -rf mongosh-1.8.0-linux-x64*

# Instalar MongoDB Hadoop Connector
RUN mkdir -p /opt/pig/lib && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongo-hadoop/mongo-hadoop-core/2.0.2/mongo-hadoop-core-2.0.2.jar -O /opt/pig/lib/mongo-hadoop-core-2.0.2.jar &&\
    wget -nv https://repo1.maven.org/maven2/org/mongodb/mongo-hadoop/mongo-hadoop-pig/2.0.2/mongo-hadoop-pig-2.0.2.jar -O /opt/pig/lib/mongo-hadoop-pig-2.0.2.jar && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/3.12.11/mongo-java-driver-3.12.11.jar  -O /opt/pig/lib/mongo-java-driver-3.12.0.jar && \
    #especifico para csv
    wget https://repo1.maven.org/maven2/org/apache/pig/piggybank/0.17.0/piggybank-0.17.0.jar -o /opt/pig/lib/piggybank-0.17.0.jar

# 2. Crear estructura de directorios primero
RUN mkdir -p /opt/hadoop/etc/hadoop && \
    mkdir -p /opt/pig/lib && \
    mkdir -p /root/.ssh && \
    mkdir -p /app

    # 3. Configuración de Hadoop (generar archivos directamente)
RUN echo '<configuration>\n\
  <property>\n\
    <name>fs.defaultFS</name>\n\
    <value>hdfs://localhost:9000</value>\n\
  </property>\n\
</configuration>' > /opt/hadoop/etc/hadoop/core-site.xml

RUN echo '<configuration>\n\
  <property>\n\
    <name>dfs.replication</name>\n\
    <value>1</value>\n\
  </property>\n\
</configuration>' > /opt/hadoop/etc/hadoop/hdfs-site.xml



# 7. Configurar entorno
ENV HADOOP_HOME=/opt/hadoop
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin:/opt/pig/bin
ENV PIG_CLASSPATH=/opt/hadoop/etc/hadoop:/opt/pig/lib/*:/opt/hadoop/share/hadoop/common/lib/*

# 8. Copiar solo los archivos necesarios
WORKDIR /app
COPY limpiar.pig .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN ls -l /opt/hadoop/bin/hdfs && ls -l /opt/pig/bin/pig


ENTRYPOINT ["/entrypoint.sh"]