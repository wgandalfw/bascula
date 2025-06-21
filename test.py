from models import get_engine, Base, CaneMovimPeso, CanePesosBalanza
from sqlalchemy.orm import sessionmaker
import os
import cx_Oracle
from sqlalchemy import text


# 🧠 Especificar la ruta al Oracle Instant Client
#cx_Oracle.init_oracle_client(lib_dir=r"F:\Python\oracle\instantclient_12_1_64")

# 🛠️ Configurar conexión
USER = "fctrinidad"
PASSWORD = "trinidad2018"
HOST = "181.80.25.12"
PORT = 10388
SERVICE_NAME = "orcl"

# 🚀 Crear engine y sesión
engine = get_engine(USER, PASSWORD, HOST, PORT, SERVICE_NAME)
Session = sessionmaker(bind=engine)
session = Session()

# 🔍 Probar consulta
try:
    resultados = session.query(CaneMovimPeso).limit(5).all()
    id = 0
    for fila in resultados:
        print(f"{id}-Zafra: {fila.zafra}, Ingenio: {fila.ingenio}, Cporte: {fila.cporte}")
        id += 1
    print ('******************************************************************************************************')
    with engine.connect() as connection:
        result = connection.execute(text("SELECT cporte, zafra, cargadero FROM CANE_MOVIM WHERE ROWNUM <= 5"))
        for row in result:
            print(f"CPORTE: {row[0]}, ZAFRA: {row[1]}, CARGADERO: {row[2]}")

    resultados = session.query(CanePesosBalanza).filter(CanePesosBalanza.vehiculo == 186).first()
    print  (resultados)
except Exception as e:
    print("❌ Error al consultar:", e)
finally:
    session.close()
