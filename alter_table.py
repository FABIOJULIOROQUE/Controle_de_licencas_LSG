import sqlite3

DB_NAME = "database.db"

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

try:
    cur.execute("ALTER TABLE licencas ADD COLUMN nome_computador TEXT;")
    print("✅ Coluna 'nome_computador' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ A coluna 'nome_computador' já existe, nada a fazer.")
    else:
        raise

con.commit()
con.close()
