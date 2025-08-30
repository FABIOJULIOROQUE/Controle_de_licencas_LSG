# set_password.py
import sys, sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB = "database.db"

def set_password(user: str, newpass: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nome TEXT UNIQUE COLLATE NOCASE,
        senha TEXT,
        is_admin INTEGER,
        representante TEXT,
        uf TEXT
    )""")
    # gerar PBKDF2 (evita diferenças de padrão como scrypt)
    h = generate_password_hash(newpass, method="pbkdf2:sha256", salt_length=16)

    cur.execute("SELECT id FROM usuarios WHERE nome=? COLLATE NOCASE", (user,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE usuarios SET senha=?, is_admin=COALESCE(is_admin,1) WHERE nome=? COLLATE NOCASE", (h, user))
        msg = "Atualizado"
    else:
        cur.execute("INSERT INTO usuarios (nome, senha, is_admin, representante, uf) VALUES (?, ?, 1, NULL, NULL)", (user, h))
        msg = "Criado"
    conn.commit()

    cur.execute("SELECT id, senha FROM usuarios WHERE nome=? COLLATE NOCASE", (user,))
    uid, saved = cur.fetchone()
    conn.close()

    print(f"{msg}: id={uid}")
    print("Hash salvo:", saved)
    print("Teste imediato:", "OK" if check_password_hash(saved, newpass) else "FALHOU")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python set_password.py <usuario> <nova_senha>")
        sys.exit(1)
    set_password(sys.argv[1].strip(), sys.argv[2])
