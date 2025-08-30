# seed_admin.py
import sqlite3
from werkzeug.security import generate_password_hash

DB = "database.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# garante tabela
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY,
  nome TEXT UNIQUE COLLATE NOCASE,
  senha TEXT,
  is_admin INTEGER,
  representante TEXT,
  uf TEXT
)""")

# cria admin se não existir
cur.execute("SELECT 1 FROM usuarios WHERE nome = 'admin'")
if not cur.fetchone():
    cur.execute(
        "INSERT INTO usuarios (nome, senha, is_admin, representante, uf) VALUES (?, ?, ?, ?, ?)",
        ("admin", generate_password_hash("admin123"), 1, None, None)
    )
    print("✅ Usuário admin criado: admin / admin123")
else:
    print("ℹ️  Usuário admin já existe")

conn.commit()
conn.close()
