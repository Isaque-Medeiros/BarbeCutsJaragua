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

        # Usar uma classe wrapper para a conexão que retorna o cursor adaptado
        class ConnectionWrapper:
            def __init__(self, original_conn):
                self._conn = original_conn
                self._cursor = CursorAdapter(original_conn.cursor())
            
            def cursor(self):
                return self._cursor
            
            def commit(self):
                self._conn.commit()
            
            def close(self):
                self._conn.close()
            
            def execute(self, query, params=None):
                return self._cursor.execute(query, params)
            
            def executemany(self, query, params_list):
                return self._cursor.executemany(query, params_list)

        return ConnectionWrapper(conn)


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
                ativo INTEGER NOT NULL DEFAULT 1,
                tipo TEXT DEFAULT 'principal'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id TEXT PRIMARY KEY,
                hash_id TEXT NOT NULL UNIQUE,
                cliente_nome TEXT NOT NULL,
                servico_id INTEGER NOT NULL,
                servicos_adicionais TEXT DEFAULT '',
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
                ativo INTEGER NOT NULL DEFAULT 1,
                tipo TEXT DEFAULT 'principal'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id TEXT PRIMARY KEY,
                hash_id TEXT NOT NULL UNIQUE,
                cliente_nome TEXT NOT NULL,
                servico_id INTEGER NOT NULL,
                servicos_adicionais TEXT DEFAULT '',
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


def run_migrations():
    """
    Executa migrações para atualizar bancos existentes.
    Isso garante que mesmo bancos já criados recebam as novas colunas/dados.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ===== Migration 1: Adicionar coluna 'tipo' se não existir =====
    if is_postgres():
        cursor.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'servicos' AND column_name = 'tipo'
                ) THEN
                    ALTER TABLE servicos ADD COLUMN tipo TEXT DEFAULT 'principal';
                END IF;
            END $$;
        ''')
    else:
        # SQLite - verificar se coluna existe
        cursor.execute("PRAGMA table_info(servicos)")
        colunas = [row[1] for row in cursor.fetchall()]
        if 'tipo' not in colunas:
            cursor.execute("ALTER TABLE servicos ADD COLUMN tipo TEXT DEFAULT 'principal'")

    # ===== Migration 1b: Garantir coluna servicos_adicionais no PostgreSQL =====
    if is_postgres():
        cursor.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'agendamentos' AND column_name = 'servicos_adicionais'
                ) THEN
                    ALTER TABLE agendamentos ADD COLUMN servicos_adicionais TEXT DEFAULT '';
                END IF;
            END $$;
        ''')
    else:
        cursor.execute("PRAGMA table_info(agendamentos)")
        colunas_ag = [row[1] for row in cursor.fetchall()]
        if 'servicos_adicionais' not in colunas_ag:
            cursor.execute("ALTER TABLE agendamentos ADD COLUMN servicos_adicionais TEXT DEFAULT ''")

    # ===== Migration 2: Atualizar serviços existentes com os dados corretos =====
    # Lista completa de serviços que devem existir
    # Organização: Cortes (principal), Adicionais, Combos
    servicos_correto = [
        # Cortes individuais
        ('Corte', 'Corte tradicional com tesoura e máquina', 30, 30.00, 'principal'),
        ('Barba', 'Aparação e modelagem de barba', 20, 20.00, 'principal'),
        ('Sobrancelha', 'Design de sobrancelha', 15, 10.00, 'principal'),
        # Adicionais (podem ser selecionados sozinhos ou como adicional)
        ('Botox', 'Botox capilar', 40, 50.00, 'adicional'),
        ('Luzes', 'Luzes com técnica profissional', 70, 60.00, 'adicional'),
        # Combos
        ('Barba + Corte', 'Barba completa com corte social', 50, 50.00, 'combo'),
        ('Barba + Sobrancelha', 'Barba com design de sobrancelha', 35, 30.00, 'combo'),
        ('Corte + Sobrancelha', 'Corte com design de sobrancelha', 45, 40.00, 'combo'),
        ('Corte + Barba + Sobrancelha', 'Corte completo, barba e sobrancelha', 65, 60.00, 'combo'),
    ]

    for nome, desc, duracao, valor, tipo in servicos_correto:
        # Verificar se o serviço já existe pelo nome
        cursor.execute('SELECT id, nome, duracao_minutos, valor, tipo FROM servicos WHERE nome = %s', (nome,))
        existing = cursor.fetchone()
        if existing:
            # Atualizar dados do serviço existente
            cursor.execute('''
                UPDATE servicos 
                SET descricao = %s, duracao_minutos = %s, valor = %s, tipo = %s, ativo = 1
                WHERE nome = %s
            ''', (desc, duracao, valor, tipo, nome))
        else:
            # Inserir novo serviço
            cursor.execute('''
                INSERT INTO servicos (nome, descricao, duracao_minutos, valor, tipo, ativo)
                VALUES (%s, %s, %s, %s, %s, 1)
            ''', (nome, desc, duracao, valor, tipo))

    # Desativar serviços antigos que não estão mais na lista
    nomes_atuais = [s[0] for s in servicos_correto]
    cursor.execute('SELECT nome FROM servicos WHERE ativo = 1')
    for row in cursor.fetchall():
        nome_existente = row['nome'] if isinstance(row, dict) else row[0]
        if nome_existente not in nomes_atuais:
            cursor.execute('UPDATE servicos SET ativo = 0 WHERE nome = %s', (nome_existente,))

    # ===== Migration 3: Atualizar intervalo_corte_minutos para 15 =====
    cursor.execute('''
        UPDATE configuracao_horarios 
        SET intervalo_corte_minutos = 15
        WHERE intervalo_corte_minutos != 15
    ''')

    # ===== Migration 4: Garantir que os horários padrão existam =====
    # ATENÇÃO: datetime.weekday() retorna: 0=Segunda, 1=Terça, ..., 5=Sábado, 6=Domingo
    horarios_padrao = [
        (0, '00:00', '00:00', 0),  # Segunda - fechado
        (1, '13:00', '20:20', 1),  # Terça
        (2, '13:00', '20:20', 1),  # Quarta
        (3, '13:00', '20:20', 1),  # Quinta
        (4, '13:00', '20:20', 1),  # Sexta
        (5, '09:00', '20:20', 1),  # Sábado
        (6, '09:00', '20:20', 1),  # Domingo
    ]

    for dia_semana, abertura, fechamento, ativo in horarios_padrao:
        cursor.execute(
            'SELECT id FROM configuracao_horarios WHERE dia_semana = %s',
            (dia_semana,)
        )
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO configuracao_horarios (dia_semana, abertura, fechamento, ativo, intervalo_corte_minutos)
                VALUES (%s, %s, %s, %s, 15)
            ''', (dia_semana, abertura, fechamento, ativo))
        else:
            # Atualizar horários existentes
            cursor.execute('''
                UPDATE configuracao_horarios 
                SET abertura = %s, fechamento = %s, ativo = %s, intervalo_corte_minutos = 15
                WHERE dia_semana = %s
            ''', (abertura, fechamento, ativo, dia_semana))

    conn.commit()
    conn.close()
    print('✅ Migrações executadas com sucesso!')


def seed_default_data():
    """Insere dados padrão se as tabelas estiverem vazias (mantido para compatibilidade)."""
    # Agora as migrações fazem todo o trabalho
    run_migrations()


if __name__ == '__main__':
    init_db()
    run_migrations()
    print('✅ Banco de dados inicializado com sucesso!')
