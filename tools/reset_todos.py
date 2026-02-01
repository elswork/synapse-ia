import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno del Nexus
load_dotenv("/home/pirate/docker/synapse-ia/.env")

def reset_and_add_todos():
    try:
        db_url = os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Borrar todas las tareas existentes
        print("Borrando tareas antiguas...")
        cur.execute("DELETE FROM todos;")
        
        # 2. Insertar las nuevas tareas
        task1_desc = """Análisis y Reestructuración del Proyecto (Gran Diseño):
1-Estructura de repositorios clara y ordenada.
2-Mejores prácticas (Arquitectura Hexagonal, DDD).
3-Seguridad de la información (Público/Privado).
4-Distribución de repositorios por hardware (GPC, HC1, M2, Legion, Chromebook)."""
        
        task1_analysis = """Propuesta del COO para frenar el crecimiento descontrolado. 
Requiere consenso Arquímedes/Athena y un plan de acción elaborado para seguir adelante de forma ordenada y segura."""

        task2_desc = "Integración de voz con Home Assistant (M2): Probar asistentes de voz aprovechando la llegada de la tarjeta de sonido y micro."
        task2_analysis = "Basado en la recomendación de Omar. El M2 ya corre HAS, evaluar viabilidad de integración."

        print("Insertando nuevas directivas...")
        cur.execute("INSERT INTO todos (description, analysis, status) VALUES (%s, %s, %s);", 
                    (task1_desc, task1_analysis, 'pending'))
        
        cur.execute("INSERT INTO todos (description, analysis, status) VALUES (%s, %s, %s);", 
                    (task2_desc, task2_analysis, 'pending'))
        
        conn.commit()
        print("¡Memoria de Postgres actualizada con éxito!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error en la operación de base de datos: {e}")

if __name__ == "__main__":
    reset_and_add_todos()
