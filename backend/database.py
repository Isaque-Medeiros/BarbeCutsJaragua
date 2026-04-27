"""
database.py — Configuração e inicialização do banco de dados
===========================================================
Gerencia a criação das tabelas e conexão com SQLite (local) e PostgreSQL (produção).
"""

import os
from datetime import datetime

# Configuração do banco de dados
def get_connection():
    """Retorna uma conexão com o banco de dados (SQLite local ou PostgreSQL produção)."""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and (
        database_url.startswith('postgres://')
        or database_url.startswith('postgresql://')
    ):
        # PostgreSQL (Neon.tech / Render / Vercel)
        import psycopg2
        import psycopg2.extras
        
        # Converter URL do Render/Neon para formato do psycopg2
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Configurar SSL para Neon.tech (exigido)
        conn = psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
            sslmode='require'
        )
        conn.autocommit = False
        return conn
    else:
        # SQLite (desenvolvimento local)
        import sqlite3
        import re
        DB_PATH = os.path.join(os.path.dirname(__file__), 'barbearia.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        
        # Adaptar o cursor do SQLite para aceitar %s como placeholder (igual PostgreSQL)
        class CursorAdapter:
            def __init__(self, cursor):
                self.cursor = cursor
                self.rowcount = 0
                self.lastrowid = None

            def execute(self, query, params=None):
                # Converter %s para ? (SQLite usa ? como placeholder)
                if params is not None:
                    sqlite_query = re.sub(r'%s', '?', query)
                    self.cursor.execute(sqlite_query, params)
                else:
                    self.cursor.execute(query)
                self.rowcount = self.cursor.rowcount
                self.lastrowid = self.cursor.lastrowid
                return self

            def executemany(self, query, params_list):
                sqlite_query = re.sub(r'%s', '?', query)
                self.cursor.executemany(sqlite_query, params_list)
                self.rowcount = self.cursor.rowcount
                return self

            def fetchone(self):
                return self.cursor.fetchone()

            def fetchall(self):
                return self.cursor.fetchall()

            def close(self):
                self.cursor.close()

        # Retornar conexão com cursor adaptado
        original_cursor = conn.cursor()
        conn._adapted_cursor = CursorAdapter(original_cursor)
        
        # Monkey-patch para que conn.cursor() retorne nosso adaptador
        original_cursor_method = conn.cursor
        def adapted_cursor():
            return conn._adapted_cursor
        conn.cursor = adapted_cursor
        
        return conn


def is_postgres():
    """Verifica se está usando PostgreSQL."""
    database_url = os.environ.get('DATABASE_URL', '')
    return database_url.startswith('postgres://') or database_url.startswith('postgresql://')


def init_db():
    """Cria as tabelas do banco de dados se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    if is_postgres():
        # PostgreSQL - usar tipo SERIAL para auto-increment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                duracao_minutos INTEGER NOT NULL,
                valor REAL NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id TEXT PRIMARY KEY,
                hash_id TEXT NOT NULL UNIQUE,
                cliente_nome TEXT NOT NULL,
                servico_id INTEGER NOT NULL,
                valor_pago REAL DEFAULT 0,
                valor_original REAL NOT NULL,
                data_hora_inicio TEXT NOT NULL,
                data_hora_fim TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'agendado',
                nota_opcional TEXT DEFAULT '',
                telefone_contato TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bloqueios (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                data_fim TEXT DEFAULT '',
                hora_inicio TEXT DEFAULT '',
                hora_fim TEXT DEFAULT '',
                motivo TEXT DEFAULT ''
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracao_horarios (
                id SERIAL PRIMARY KEY,
                dia_semana INTEGER NOT NULL,
                abertura TEXT NOT NULL,
                fechamento TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                intervalo_corte_minutos INTEGER NOT NULL DEFAULT 30
            )
        ''')

        # Índices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_data
            ON agendamentos(data_hora_inicio)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_hash
            ON agendamentos(hash_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_status
            ON agendamentos(status)
        ''')
    else:
        # SQLite
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                duracao_minutos INTEGER NOT NULL,
                valor REAL NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id TEXT PRIMARY KEY,
                hash_id TEXT NOT NULL UNIQUE,
                cliente_nome TEXT NOT NULL,
                servico_id INTEGER NOT NULL,
                valor_pago REAL DEFAULT 0,
                valor_original REAL NOT NULL,
                data_hora_inicio TEXT NOT NULL,
                data_hora_fim TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'agendado',
                nota_opcional TEXT DEFAULT '',
                telefone_contato TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bloqueios (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                data_fim TEXT DEFAULT '',
                hora_inicio TEXT DEFAULT '',
                hora_fim TEXT DEFAULT '',
                motivo TEXT DEFAULT ''
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracao_horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_semana INTEGER NOT NULL,
                abertura TEXT NOT NULL,
                fechamento TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                intervalo_corte_minutos INTEGER NOT NULL DEFAULT 30
            )
        ''')

        # Índices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_data
            ON agendamentos(data_hora_inicio)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_hash
            ON agendamentos(hash_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agendamentos_status
            ON agendamentos(status)
        ''')

    conn.commit()
    conn.close()


def seed_default_data():
    """Insere dados padrão se as tabelas estiverem vazias."""
    conn = get_connection()
    cursor = conn.cursor()

    # Serviços padrão
    cursor.execute('SELECT COUNT(*) as total FROM servicos')
    row = cursor.fetchone()
    if row['total'] == 0:
        servicos = [
            ('Corte Social', 'Corte tradicional com tesoura e máquina', 30, 35.00),
            ('Barba', 'Aparação e modelagem de barba', 20, 20.00),
            ('Combo Corte + Barba', 'Corte social completo com barba', 50, 50.00),
            ('Degradê', 'Corte degradê americano ou social', 40, 45.00),
            ('Hidratação Capilar', 'Hidratação completa dos fios', 30, 30.00),
        ]
        cursor.executemany(
            'INSERT INTO servicos (nome, descricao, duracao_minutos, valor) VALUES (%s, %s, %s, %s)',
            servicos
        )

    # Horários padrão (seg-sáb 08:00-21:30, dom 08:00-18:00)
    cursor.execute('SELECT COUNT(*) as total FROM configuracao_horarios')
    row = cursor.fetchone()
    if row['total'] == 0:
        horarios = [
            (0, '08:00', '18:00', 1, 30),  # Domingo
            (1, '08:00', '21:30', 1, 30),  # Segunda
            (2, '08:00', '21:30', 1, 30),  # Terça
            (3, '08:00', '21:30', 1, 30),  # Quarta
            (4, '08:00', '21:30', 1, 30),  # Quinta
            (5, '08:00', '21:30', 1, 30),  # Sexta
            (6, '08:00', '21:30', 1, 30),  # Sábado
        ]
        cursor.executemany(
            'INSERT INTO configuracao_horarios (dia_semana, abertura, fechamento, ativo, intervalo_corte_minutos) VALUES (%s, %s, %s, %s, %s)',
            horarios
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    seed_default_data()
    print('✅ Banco de dados inicializado com sucesso!')
