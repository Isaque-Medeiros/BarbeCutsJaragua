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
        # PostgreSQL (Render)
        import psycopg2
        import psycopg2.extras
        
        # Converter URL do Render para formato do psycopg2
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        conn.autocommit = False
        return conn
    else:
        # SQLite (desenvolvimento local)
        import sqlite3
        DB_PATH = os.path.join(os.path.dirname(__file__), 'barbearia.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn


def init_db():
    """Cria as tabelas do banco de dados se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela: servicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR NOT NULL,
            descricao TEXT DEFAULT '',
            duracao_minutos INTEGER NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # Tabela: agendamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id VARCHAR PRIMARY KEY,
            hash_id VARCHAR NOT NULL UNIQUE,
            cliente_nome VARCHAR NOT NULL,
            servico_id INTEGER NOT NULL,
            valor_pago DECIMAL(10,2) DEFAULT 0,
            valor_original DECIMAL(10,2) NOT NULL,
            data_hora_inicio TIMESTAMP NOT NULL,
            data_hora_fim TIMESTAMP NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'agendado',
            nota_opcional TEXT DEFAULT '',
            telefone_contato VARCHAR DEFAULT '',
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (servico_id) REFERENCES servicos(id)
        )
    ''')

    # Tabela: bloqueios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios (
            id VARCHAR PRIMARY KEY,
            data DATE NOT NULL,
            hora_inicio VARCHAR DEFAULT '',
            hora_fim VARCHAR DEFAULT '',
            motivo TEXT DEFAULT ''
        )
    ''')

    # Tabela: configuracao_horarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracao_horarios (
            id SERIAL PRIMARY KEY,
            dia_semana INTEGER NOT NULL,
            abertura VARCHAR NOT NULL,
            fechamento VARCHAR NOT NULL,
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
    cursor.execute('SELECT COUNT(*) AS total FROM servicos')
    if cursor.fetchone()['total'] == 0:
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

    # Horários padrão (seg-sex 08:00-19:00, sáb 08:00-17:00)
    cursor.execute('SELECT COUNT(*) AS total FROM configuracao_horarios')
    if cursor.fetchone()['total'] == 0:
        horarios = [
            (0, '00:00', '00:00', 0, 30),  # Domingo - fechado
            (1, '08:00', '19:00', 1, 30),  # Segunda
            (2, '08:00', '19:00', 1, 30),  # Terça
            (3, '08:00', '19:00', 1, 30),  # Quarta
            (4, '08:00', '19:00', 1, 30),  # Quinta
            (5, '08:00', '19:00', 1, 30),  # Sexta
            (6, '08:00', '17:00', 1, 30),  # Sábado
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
