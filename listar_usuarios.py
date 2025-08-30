import sqlite3

DB_NAME = "database.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("SELECT id, nome, senha, is_admin, representante, uf FROM usuarios")
rows = cur.fetchall()
conn.close()

print("=== USUÁRIOS CADASTRADOS ===")
for r in rows:
    print(f"ID={r[0]}, Nome={r[1]}, Senha={r[2]}, Admin={r[3]}, Rep={r[4]}, UF={r[5]}")
