import sqlite3
import datetime

DB_NAME = "database.db"

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

# Apaga tabelas existentes
cur.execute("DROP TABLE IF EXISTS licencas")
cur.execute("DROP TABLE IF EXISTS usuarios")
cur.execute("DROP TABLE IF EXISTS logs")

# Cria tabela de usuários
cur.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'user',
        representante TEXT,
        estado TEXT,
        cidade TEXT
    )
""")

# Cria tabela de licenças
cur.execute("""
    CREATE TABLE licencas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        responsavel TEXT,
        setor TEXT,
        representante TEXT,
        cidade TEXT,
        estado TEXT,
        tipo TEXT,
        codigo_manutencao TEXT,
        nome_computador TEXT,
        data_import TEXT
    )
""")

# Cria tabela de logs
cur.execute("""
    CREATE TABLE logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        acao TEXT,
        data_hora TEXT
    )
""")

con.commit()
con.close()

print(f"✅ Banco reiniciado em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}!")
