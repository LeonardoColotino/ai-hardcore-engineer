import sqlite3

from app.config import settings


def get_connection():
    """
    Cria uma conexão com o banco SQLite.
    """
    return sqlite3.connect(settings.DATABASE_NAME)


def initialize_payments():
    """
    Cria a tabela de pagamentos e adiciona dados fictícios.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            deposit_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM payments
        """
    )

    total = cursor.fetchone()[0]

    if total == 0:

        payments = [
            (
                "cliente1988",
                250.90,
                "2026-08-30",
                "2026-09-01",
                "scheduled"
            ),
            (
                "cliente1988",
                480.00,
                "2026-08-29",
                "2026-08-31",
                "paid"
            ),
            (
                "cliente2001",
                130.50,
                "2026-08-30",
                "2026-09-01",
                "scheduled"
            )
        ]

        cursor.executemany(
            """
            INSERT INTO payments (
                user_id,
                amount,
                sale_date,
                deposit_date,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            payments
        )

    connection.commit()
    connection.close()


def get_payments(user_id: str) -> list[dict]:


    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            amount,
            sale_date,
            deposit_date,
            status
        FROM payments
        WHERE user_id = ?
        ORDER BY sale_date DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "amount": row[1],
            "sale_date": row[2],
            "deposit_date": row[3],
            "status": row[4]
        }
        for row in rows
    ]