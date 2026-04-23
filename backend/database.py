"""
database.py — Configuração e inicialização do banco SQLite
===========================================================
Gerencia a criação das tabelas e conexão com o banco de dados.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'barbearia.db')


def get_connection():
    """Retorna uma conexão com o banco SQLite."""
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT DEFAULT '',
            duracao_minutos INTEGER NOT NULL,
            valor REAL NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # Tabela: agendamentos
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

    # Tabela: bloqueios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bloqueios (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            hora_inicio TEXT DEFAULT '',
            hora_fim TEXT DEFAULT '',
            motivo TEXT DEFAULT ''
        )
    ''')

    # Tabela: configuracao_horarios
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
    cursor.execute('SELECT COUNT(*) FROM servicos')
    if cursor.fetchone()[0] == 0:
        servicos = [
            ('Corte Social', 'Corte tradicional com tesoura e máquina', 30, 35.00),
            ('Barba', 'Aparação e modelagem de barba', 20, 20.00),
            ('Combo Corte + Barba', 'Corte social completo com barba', 50, 50.00),
            ('Degradê', 'Corte degradê americano ou social', 40, 45.00),
            ('Hidratação Capilar', 'Hidratação completa dos fios', 30, 30.00),
        ]
        cursor.executemany(
            'INSERT INTO servicos (nome, descricao, duracao_minutos, valor) VALUES (?, ?, ?, ?)',
            servicos
        )

    # Horários padrão (seg-sex 08:00-19:00, sáb 08:00-17:00)
    cursor.execute('SELECT COUNT(*) FROM configuracao_horarios')
    if cursor.fetchone()[0] == 0:
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
            'INSERT INTO configuracao_horarios (dia_semana, abertura, fechamento, ativo, intervalo_corte_minutos) VALUES (?, ?, ?, ?, ?)',
            horarios
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    seed_default_data()
    print('✅ Banco de dados inicializado com sucesso!')
