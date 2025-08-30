# check_password.py
import sqlite3
from werkzeug.security import check_password_hash

DB = "database.db"
USER = "admin"          # mude se quiser conferir outro usuário
TEST_PW = "admin123"    # senha que você está tentando no login

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id, nome, senha FROM usuarios WHERE nome=? COLLATE NOCASE", (USER,))
row = cur.fetchone()
con.close()

if not row:
    print(f"Usuário '{USER}' não encontrado.")
else:
    uid, nome, hash_db = row
    print(f"ID={uid}  nome='{nome}'")
    print(f"Hash no banco: {hash_db}")
    ok = hash_db and hash_db.startswith("pbkdf2:") and check_password_hash(hash_db, TEST_PW)
    print("Resultado do check_password_hash:", "OK (senha confere)" if ok else "FALHOU (senha não confere)")
