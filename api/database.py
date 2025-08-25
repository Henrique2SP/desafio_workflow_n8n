import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DATABASE_URL = os.getenv("DATABASE_URL")
connection_pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)

@contextmanager
def get_db_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

def init_db():
    """Cria a tabela única de eventos com as colunas corretas."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS eventos (
        id SERIAL PRIMARY KEY,
        evento VARCHAR(255) NOT NULL,
        data VARCHAR(255),
        descricao TEXT,
        engajamento INT,
        status VARCHAR(100),
        origem VARCHAR(50)
    );
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()

def create_evento(evento_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insere um novo evento na tabela 'eventos'."""
    query = """
    INSERT INTO eventos (evento, data, descricao, engajamento, status, origem)
    VALUES (%(evento)s, %(data)s, %(descricao)s, %(engajamento)s, %(status)s, %(origem)s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, evento_data)
            new_evento = cursor.fetchone()
            conn.commit()
            return dict(new_evento)

def get_all_eventos() -> List[Dict[str, Any]]:
    query = "SELECT * FROM eventos ORDER BY id;"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            eventos = cursor.fetchall()
            return [dict(row) for row in eventos]

def get_evento_by_id(evento_id: int) -> Optional[Dict[str, Any]]:
    """Busca um único evento pelo seu ID."""
    query = "SELECT * FROM eventos WHERE id = %s;"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (evento_id,))
            evento = cursor.fetchone()
            return dict(evento) if evento else None

def update_evento(evento_id: int, evento_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Atualiza um evento existente."""
    update_data = {k: v for k, v in evento_data.items() if v is not None}
    if not update_data:
        return get_evento_by_id(evento_id)

    set_clause = ", ".join([f"{key} = %({key})s" for key in update_data.keys()])
    query = f"UPDATE eventos SET {set_clause} WHERE id = %(id)s RETURNING *;"
    update_data['id'] = evento_id
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, update_data)
            updated_evento = cursor.fetchone()
            conn.commit()
            return dict(updated_evento) if updated_evento else None

def delete_evento(evento_id: int) -> bool:
    """Deleta um evento pelo seu ID."""
    query = "DELETE FROM eventos WHERE id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (evento_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted