"""
Ferramenta de consulta de dados do cliente.
"""

import sqlite3

from app.config import settings


def get_connection():
    """
    Cria uma conexão com o banco SQLite.
    """
    return sqlite3.connect(settings.DATABASE_NAME)


def initialize_database():
    """
    Cria a tabela de clientes e insere dados fictícios
    caso ainda não existam.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan TEXT NOT NULL,
            machine_model TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    customers = [
        (
            "cliente1988",
            "João Silva",
            "Get Smart",
            "POS Smart",
            "active"
        ),
        (
            "cliente2001",
            "Maria Souza",
            "Get Clássica",
            "POS Clássica",
            "active"
        )
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO customers (
            user_id,
            name,
            plan,
            machine_model,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        customers
    )

    connection.commit()
    connection.close()


def get_customer(user_id: str) -> dict | None:
    """
    Busca os dados de um cliente pelo user_id.

    Args:
        user_id: Identificador do usuário.

    Returns:
        Dicionário com dados do cliente ou None.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            name,
            plan,
            machine_model,
            status
        FROM customers
        WHERE user_id = ?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "name": row[1],
        "plan": row[2],
        "machine_model": row[3],
        "status": row[4]
    }