# Proyecto_BDNR_ApuestasDeportivas
## Integrantes: 
    José Israel León Zermeño--758192    
    Yeshua Miranda Morales-- 758258
    Carlos Omar Barajas Barragan-- 

## Breve descripción del proyecto (qué hará, para qué).
La aplicación que vamos a replicar a partir de la base de datos es una casa de apuestas deportivas enfocada en fútbol, en la que existe un usuario apostador. El scope general del proyecto es que la aplicación funcione de forma correcta y consistente en las tres bases de datos del sistema (Cassandra, MongoDB y Dgraph).  Cassandra se enfoca en consultas de datos más recientes usando como pk la temporada actual, basadas en valores máximos y mínimos, como los jugadores con más goles. MongoDB se enfoca en el historial completo de la información de jugadores, usuarios, equipos y ligas, como los goles anotados por un jugador, las apuestas y transacciones de un usuario o los partidos de un equipo. Dgraph se enfoca en las relaciones entre los datos, como las conexiones entre usuarios, jugadores, equipos, ligas y apuestas, para obtener recomendaciones y consultas basadas en dichas conexiones. Quedan fuera del alcance el registro e inicio de sesión de usuarios, otros deportes distintos al fútbol, la integración con pasarelas de pago reales, la aplicación móvil nativa, la transmisión de partidos en vivo y las validaciones legales o regulatorias

## Flujo de trabajo (que se corre para insertar datos, cómo se van a correr las consultas etc) Nota: Este lo pueden mejorar conforme avancen en el proyecto, ahorita es un draft inicial.
La carga inicial de datos se realizará mediante archivos JSON, los cuales servirán como fuente principal para poblar las bases de datos MongoDB y Dgraph. Posteriormente, esta información se exportará y organizará en archivos de Excel para facilitar su revisión, validación y adaptación al formato requerido por Cassandra.
Una vez cargada la información, las consultas se ejecutarán desde una interfaz gráfica que funcionará como punto de interacción para el usuario. Las funcionalidades estarán organizadas de acuerdo con las necesidades de la aplicación y no dependerán directamente de una base de datos en particular. Es decir, el usuario podrá acceder a las distintas funcionalidades sin necesidad de conocer qué base de datos se utiliza para obtener la información.
A nivel interno, cada funcionalidad se comunicará con la base de datos correspondiente según el tipo de información que necesite consultar o modificar. De esta manera, se busca aprovechar las fortalezas de Cassandra, MongoDB y Dgraph, manteniendo una experiencia de usuario consistente y centralizada.

# Entorno de Bases de Datos - Casa de Apuestas

Este proyecto utiliza MongoDB, Apache Cassandra y Dgraph. Todo el ecosistema está orquestado mediante Docker Compose para facilitar el desarrollo local.

## 1. Levantar los contenedores de Docker

Antes de ejecutar el código en Python, necesitas levantar las bases de datos. Abre tu terminal en la raíz de este proyecto y ejecuta:

```bash
docker-compose up -d
```

## 2. Crear y activar el Entorno Virtual de Python

```bash
py -3.10 -m venv ./venv
```
## 3. Activar el entorno virtual

Si usas Git Bash o WSL (Ubuntu):

```bash
source venv/bin/activate
```

Si usas PowerShell (Windows):

```bash
.\venv\Scripts\Activate.ps1
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```