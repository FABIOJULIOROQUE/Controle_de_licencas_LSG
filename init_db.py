import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

# Exemplo de tabela usuarios
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    representante TEXT,
    uf TEXT
)
""")

# Usuário admin padrão
cur.execute("""
INSERT INTO usuarios (nome, senha, is_admin, representante, uf)
VALUES ('admin', 'admin', 1, 'Master', 'BR')
""")

con.commit()
con.close()

print("✅ Banco de dados inicializado com sucesso!")
