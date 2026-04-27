"""
app.py — API Flask do Sistema de Agendamento
=============================================
Endpoints públicos e administrativos para o sistema da barbearia.
"""

import os
import json
from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from database import get_connection, init_db, seed_default_data, is_postgres
from services import (
    gerar_hash_id, gerar_id, calcular_slots_disponiveis,
    validar_agendamento, calcular_resumo_financeiro,
    formatar_mensagem_whatsapp, formatar_data_br,
    formatar_hora_br, time_to_minutes
)

app = Flask(__name__, static_folder=None)
CORS(app)
_db_initialized = False


# ===================== CONVERSOR DE DATAS PARA JSON =====================

def converter_datas(obj):
    """Converte recursivamente objetos datetime/date para string ISO em dicts e listas."""
    if isinstance(obj, dict):
        return {k: converter_datas(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_datas(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def jsonify_com_datas(*args, **kwargs):
    """jsonify que converte automaticamente datetime/date para string ISO."""
    data = converter_datas(args[0] if args else kwargs)
    return jsonify(data)



# ===================== TRATAMENTO DE ERROS GLOBAL =====================


@app.errorhandler(Exception)
def handle_exception(e):
    """Captura qualquer exceção não tratada e retorna JSON."""
    import traceback
    print(f'[ERRO] {traceback.format_exc()}')
    return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500


@app.errorhandler(500)
def handle_500(e):
    """Garante que erro 500 retorne JSON."""
    return jsonify({'erro': 'Erro interno do servidor.'}), 500


@app.errorhandler(404)
def handle_404(e):
    """Garante que erro 404 em APIs retorne JSON."""
    if request.path.startswith('/api/'):
        return jsonify({'erro': 'Endpoint não encontrado.'}), 404
    return e


# Configurações
ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'admbarber1904')
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '5511972244484')
BARBEARIA_NOME = os.environ.get('BARBEARIA_NOME', 'Barbearia do Seu Zé')

# Caminho para o frontend
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend')


# ===================== ROTAS DO FRONTEND =====================

@app.route('/')
def index():
    return send_from_directory(FRONTEND_PATH, 'index.html')


@app.route('/admin')
def admin_page():
    return send_from_directory(FRONTEND_PATH, 'admin.html')


@app.route('/agendamento')
def agendamento_page():
    return send_from_directory(FRONTEND_PATH, 'agendamento.html')


@app.route('/meu-agendamento')
def meu_agendamento_page():
    return send_from_directory(FRONTEND_PATH, 'meu-agendamento.html')


@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'css'), filename)


@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'js'), filename)


@app.route('/img/<path:filename>')
def img_files(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'img'), filename)


# ===================== ENDPOINTS PÚBLICOS =====================

@app.route('/api/servicos', methods=['GET'])
def listar_servicos():
    """Lista todos os serviços ativos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicos WHERE ativo = 1 ORDER BY nome')
    servicos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify_com_datas({'servicos': servicos})


@app.route('/api/horarios', methods=['GET'])
def buscar_horarios():
    """
    Busca slots disponíveis para uma data e serviço.
    Query params: data (YYYY-MM-DD), servicoId
    """
    data_str = request.args.get('data', '')
    servico_id = request.args.get('servicoId', type=int)

    if not data_str or not servico_id:
        return jsonify({'erro': 'Parâmetros data e servicoId são obrigatórios.'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Buscar serviço
    cursor.execute('SELECT * FROM servicos WHERE id = %s AND ativo = 1', (servico_id,))
    servico = cursor.fetchone()
    if not servico:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404
    servico = dict(servico)

    # Descobrir dia da semana
    try:
        dt = datetime.strptime(data_str, '%Y-%m-%d')
        dia_semana = dt.weekday()
    except:
        conn.close()
        return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD.'}), 400

    # Buscar configuração de horário para o dia da semana
    cursor.execute(
        'SELECT * FROM configuracao_horarios WHERE dia_semana = %s',
        (dia_semana,)
    )
    config_horario = cursor.fetchone()
    config_horario = dict(config_horario) if config_horario else None

    if not config_horario or not config_horario.get('ativo'):
        conn.close()
        return jsonify({
            'data': data_str,
            'diaSemana': dia_semana,
            'servico': servico,
            'horarioFuncionamento': None,
            'slotsDisponiveis': []
        })

    # Buscar agendamentos existentes para a data
    data_inicio = f"{data_str}T00:00:00"
    data_fim = f"{data_str}T23:59:59"
    cursor.execute(
        'SELECT * FROM agendamentos WHERE data_hora_inicio >= %s AND data_hora_inicio <= %s',
        (data_inicio, data_fim)
    )
    agendamentos = [dict(row) for row in cursor.fetchall()]

    # Buscar bloqueios para a data
    cursor.execute('SELECT * FROM bloqueios WHERE data = %s', (data_str,))
    bloqueios = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # Calcular slots disponíveis
    slots = calcular_slots_disponiveis(
        data=data_str,
        servico_id=servico_id,
        servico_duracao=servico['duracao_minutos'],
        servico_buffer=config_horario['intervalo_corte_minutos'],
        config_horario=config_horario,
        agendamentos_existentes=agendamentos,
        bloqueios=bloqueios
    )

    return jsonify({
        'data': data_str,
        'diaSemana': dia_semana,
        'servico': servico,
        'horarioFuncionamento': {
            'abertura': config_horario['abertura'],
            'fechamento': config_horario['fechamento'],
            'intervalo': config_horario['intervalo_corte_minutos']
        },
        'slotsDisponiveis': slots
    })


@app.route('/api/agendamentos', methods=['POST'])
def criar_agendamento():
    """Cria um novo agendamento."""
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'Dados são obrigatórios.'}), 400

    cliente_nome = dados.get('clienteNome', '').strip()
    servico_id = dados.get('servicoId')
    data_hora_inicio = dados.get('dataHoraInicio', '')
    nota_opcional = dados.get('notaOpcional', '').strip()
    telefone_contato = dados.get('telefoneContato', '').strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Buscar serviço
    cursor.execute('SELECT * FROM servicos WHERE id = %s AND ativo = 1', (servico_id,))
    servico = cursor.fetchone()
    if not servico:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404
    servico = dict(servico)

    # Descobrir dia da semana
    try:
        dt = datetime.fromisoformat(data_hora_inicio)
        dia_semana = dt.weekday()
    except:
        conn.close()
        return jsonify({'erro': 'Formato de data/hora inválido.'}), 400

    # Buscar configuração de horário
    cursor.execute(
        'SELECT * FROM configuracao_horarios WHERE dia_semana = %s',
        (dia_semana,)
    )
    config_horario = cursor.fetchone()
    config_horario = dict(config_horario) if config_horario else None

    # Calcular data_hora_fim
    buffer = config_horario['intervalo_corte_minutos'] if config_horario else 30
    duracao_total = servico['duracao_minutos'] + buffer
    dt_inicio = datetime.fromisoformat(data_hora_inicio)
    dt_fim = dt_inicio + timedelta(minutes=duracao_total)
    data_hora_fim = dt_fim.isoformat()

    # Buscar agendamentos conflitantes
    cursor.execute('''
        SELECT * FROM agendamentos
        WHERE data_hora_inicio < %s AND data_hora_fim > %s
        AND status != 'cancelado'
    ''', (data_hora_fim, data_hora_inicio))
    conflitantes = [dict(row) for row in cursor.fetchall()]

    # Buscar bloqueios para a data
    data_str = dt_inicio.strftime('%Y-%m-%d')
    cursor.execute('SELECT * FROM bloqueios WHERE data = %s', (data_str,))
    bloqueios = [dict(row) for row in cursor.fetchall()]

    # Validar agendamento
    validacao = validar_agendamento(
        cliente_nome=cliente_nome,
        data_hora_inicio=data_hora_inicio,
        servico_id=servico_id,
        servico_duracao=servico['duracao_minutos'],
        servico_buffer=buffer,
        config_horario=config_horario,
        agendamentos_conflitantes=conflitantes,
        bloqueios=bloqueios
    )

    if not validacao['valido']:
        conn.close()
        return jsonify({'erro': validacao['erro']}), 409

    # Criar agendamento
    agora = datetime.now().isoformat()
    ag_id = gerar_id()
    hash_id = gerar_hash_id()

    cursor.execute('''
        INSERT INTO agendamentos
        (id, hash_id, cliente_nome, servico_id, valor_pago, valor_original,
         data_hora_inicio, data_hora_fim, status, nota_opcional,
         telefone_contato, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        ag_id, hash_id, cliente_nome, servico_id, 0, servico['valor'],
        data_hora_inicio, data_hora_fim, 'agendado', nota_opcional,
        telefone_contato, agora, agora
    ))

    conn.commit()
    conn.close()

    # Formatar mensagem do WhatsApp
    data_br = formatar_data_br(data_hora_inicio)
    hora_inicio = formatar_hora_br(data_hora_inicio)
    hora_fim = formatar_hora_br(data_hora_fim)

    mensagem = formatar_mensagem_whatsapp(
        cliente_nome=cliente_nome,
        data=data_br,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        servico_nome=servico['nome'],
        valor=servico['valor'],
        nota_opcional=nota_opcional,
        url_site=SITE_URL
    )

    # URL do WhatsApp
    import urllib.parse
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensagem)}"

    return jsonify({
        'success': True,
        'agendamento': {
            'hashId': hash_id,
            'clienteNome': cliente_nome,
            'servico': servico['nome'],
            'servicoId': servico_id,
            'dataHoraInicio': data_hora_inicio,
            'dataHoraFim': data_hora_fim,
            'valor': servico['valor'],
            'status': 'agendado',
            'notaOpcional': nota_opcional,
            'mensagemWhatsApp': mensagem,
            'whatsappUrl': whatsapp_url
        }
    }), 201


@app.route('/api/agendamentos/consulta', methods=['GET'])
def consultar_agendamento():
    """Consulta um agendamento pelo hash ID."""
    hash_id = request.args.get('hash', '')

    if not hash_id:
        return jsonify({'erro': 'Hash ID é obrigatório.'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, s.nome as servico_nome, s.duracao_minutos
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.hash_id = %s
    ''', (hash_id,))
    agendamento = cursor.fetchone()
    conn.close()

    if not agendamento:
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404

    ag = dict(agendamento)
    return jsonify({
        'agendamento': {
            'hashId': ag['hash_id'],
            'clienteNome': ag['cliente_nome'],
            'servico': ag['servico_nome'],
            'dataHoraInicio': ag['data_hora_inicio'],
            'dataHoraFim': ag['data_hora_fim'],
            'valor': ag['valor_original'],
            'valorPago': ag['valor_pago'],
            'status': ag['status'],
            'notaOpcional': ag['nota_opcional'],
            'createdAt': ag['created_at']
        }
    })


@app.route('/api/config/horarios', methods=['GET'])
def get_config_horarios():
    """Retorna a configuração de horários de funcionamento."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM configuracao_horarios ORDER BY dia_semana')
    horarios = [dict(row) for row in cursor.fetchall()]
    conn.close()

    dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    for h in horarios:
        h['diaNome'] = dias[h['dia_semana']]

    return jsonify({'configHorarios': horarios})


# ===================== ENDPOINTS ADMIN =====================

def verificar_admin():
    """Verifica se o header de admin secret é válido."""
    secret = request.headers.get('x-admin-secret', '')
    return secret == ADMIN_SECRET


@app.route('/api/admin/agendamentos', methods=['GET'])
def admin_listar_agendamentos():
    """Lista agendamentos com filtros (admin)."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    periodo = request.args.get('periodo', 'hoje')
    data_inicio = request.args.get('dataInicio', '')
    data_fim = request.args.get('dataFim', '')

    conn = get_connection()
    cursor = conn.cursor()

    hoje = date.today().isoformat()

    if periodo == 'hoje':
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{hoje}T00:00:00", f"{hoje}T23:59:59"]
    elif periodo == 'semana':
        inicio_semana = (date.today() - timedelta(days=date.today().weekday())).isoformat()
        fim_semana = (date.today() + timedelta(days=6 - date.today().weekday())).isoformat()
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{inicio_semana}T00:00:00", f"{fim_semana}T23:59:59"]
    elif periodo == 'mes':
        inicio_mes = date.today().replace(day=1).isoformat()
        where = "WHERE a.data_hora_inicio >= %s"
        params = [f"{inicio_mes}T00:00:00"]
    elif periodo == 'personalizado' and data_inicio and data_fim:
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{data_inicio}T00:00:00", f"{data_fim}T23:59:59"]
    else:
        # 'todos' ou qualquer outro valor - sem filtro de data
        where = ""
        params = []

    query = f'''
        SELECT a.*, s.nome as servico_nome, s.duracao_minutos
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        {where}
        ORDER BY a.data_hora_inicio ASC
    '''

    cursor.execute(query, params)
    agendamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify_com_datas({'agendamentos': agendamentos})


@app.route('/api/admin/financeiro', methods=['GET'])
def admin_financeiro():
    """Retorna resumo financeiro do período."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    periodo = request.args.get('periodo', 'hoje')
    data_inicio = request.args.get('dataInicio', '')
    data_fim = request.args.get('dataFim', '')

    conn = get_connection()
    cursor = conn.cursor()

    hoje = date.today().isoformat()

    if periodo == 'hoje':
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{hoje}T00:00:00", f"{hoje}T23:59:59"]
    elif periodo == 'semana':
        inicio_semana = (date.today() - timedelta(days=date.today().weekday())).isoformat()
        fim_semana = (date.today() + timedelta(days=6 - date.today().weekday())).isoformat()
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{inicio_semana}T00:00:00", f"{fim_semana}T23:59:59"]
    elif periodo == 'mes':
        inicio_mes = date.today().replace(day=1).isoformat()
        where = "WHERE a.data_hora_inicio >= %s"
        params = [f"{inicio_mes}T00:00:00"]
    elif periodo == 'personalizado' and data_inicio and data_fim:
        where = "WHERE a.data_hora_inicio >= %s AND a.data_hora_inicio <= %s"
        params = [f"{data_inicio}T00:00:00", f"{data_fim}T23:59:59"]
    else:
        where = ""
        params = []

    cursor.execute(
        f'SELECT a.*, s.nome as servico_nome FROM agendamentos a JOIN servicos s ON a.servico_id = s.id {where}',
        params
    )
    agendamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    resumo = calcular_resumo_financeiro(agendamentos)
    return jsonify(resumo)


@app.route('/api/admin/agendamentos/<ag_id>', methods=['PUT'])
def admin_atualizar_agendamento(ag_id):
    """Atualiza valor pago e/ou status de um agendamento."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados são obrigatórios.'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if 'valorPago' in dados:
        updates.append('valor_pago = %s')
        params.append(dados['valorPago'])

    if 'status' in dados:
        status_validos = ['agendado', 'concluido', 'cancelado', 'ausente']
        if dados['status'] not in status_validos:
            conn.close()
            return jsonify({'erro': f'Status inválido. Use: {", ".join(status_validos)}'}), 400
        updates.append('status = %s')
        params.append(dados['status'])

    if not updates:
        conn.close()
        return jsonify({'erro': 'Nenhum campo para atualizar.'}), 400

    updates.append('updated_at = %s')
    params.append(datetime.now().isoformat())
    params.append(ag_id)

    cursor.execute(
        f'UPDATE agendamentos SET {", ".join(updates)} WHERE id = %s',
        params
    )

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/admin/agendamentos/cancelados', methods=['DELETE'])
def admin_limpar_cancelados():
    """Remove todos os agendamentos com status 'cancelado'."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE status = 'cancelado'")
    count = cursor.rowcount
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'removidos': count})


@app.route('/api/admin/agendamentos/<ag_id>', methods=['DELETE'])
def admin_cancelar_agendamento(ag_id):
    """Cancela um agendamento (soft delete: muda status)."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE agendamentos SET status = %s, updated_at = %s WHERE id = %s',
        ('cancelado', datetime.now().isoformat(), ag_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


# ===================== CRUD DE SERVIÇOS (ADMIN) =====================

@app.route('/api/admin/servicos', methods=['GET'])
def admin_listar_servicos():
    """Lista todos os serviços (inclusive inativos)."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servicos ORDER BY nome')
    servicos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'servicos': servicos})


@app.route('/api/admin/servicos', methods=['POST'])
def admin_criar_servico():
    """Cria um novo serviço."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados são obrigatórios.'}), 400

    nome = dados.get('nome', '').strip()
    duracao = dados.get('duracaoMinutos')
    valor = dados.get('valor')
    descricao = dados.get('descricao', '').strip()

    if not nome or not duracao or valor is None:
        return jsonify({'erro': 'Nome, duração e valor são obrigatórios.'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO servicos (nome, descricao, duracao_minutos, valor) VALUES (%s, %s, %s, %s)',
        (nome, descricao, duracao, valor)
    )
    conn.commit()

    # Obter o ID do serviço inserido (compatível com PostgreSQL e SQLite)
    if is_postgres():
        cursor.execute('SELECT LASTVAL() as id')
        servico_id = cursor.fetchone()['id']
    else:
        servico_id = cursor.lastrowid

    conn.close()

    return jsonify({'success': True, 'servico': {'id': servico_id, 'nome': nome}}), 201


@app.route('/api/admin/servicos/<int:servico_id>', methods=['PUT'])
def admin_atualizar_servico(servico_id):
    """Atualiza um serviço."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados são obrigatórios.'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if 'nome' in dados:
        updates.append('nome = %s')
        params.append(dados['nome'])
    if 'descricao' in dados:
        updates.append('descricao = %s')
        params.append(dados['descricao'])
    if 'duracaoMinutos' in dados:
        updates.append('duracao_minutos = %s')
        params.append(dados['duracaoMinutos'])
    if 'valor' in dados:
        updates.append('valor = %s')
        params.append(dados['valor'])
    if 'ativo' in dados:
        updates.append('ativo = %s')
        params.append(1 if dados['ativo'] else 0)

    if not updates:
        conn.close()
        return jsonify({'erro': 'Nenhum campo para atualizar.'}), 400

    params.append(servico_id)
    cursor.execute(
        f'UPDATE servicos SET {", ".join(updates)} WHERE id = %s',
        params
    )

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/admin/servicos/<int:servico_id>', methods=['DELETE'])
def admin_desativar_servico(servico_id):
    """Desativa um serviço (soft delete)."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE servicos SET ativo = 0 WHERE id = %s', (servico_id,))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/admin/servicos/<int:servico_id>/reativar', methods=['POST'])
def admin_reativar_servico(servico_id):
    """Reativa um serviço desativado."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE servicos SET ativo = 1 WHERE id = %s', (servico_id,))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/admin/servicos/<int:servico_id>/permanentemente', methods=['DELETE'])
def admin_excluir_servico_permanentemente(servico_id):
    """Exclui permanentemente um serviço (hard delete)."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM servicos WHERE id = %s', (servico_id,))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Serviço não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


# ===================== CRUD DE BLOQUEIOS (ADMIN) =====================

@app.route('/api/admin/bloqueios', methods=['GET'])
def admin_listar_bloqueios():
    """Lista todos os bloqueios."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bloqueios ORDER BY data DESC')
    bloqueios = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'bloqueios': bloqueios})


@app.route('/api/admin/bloqueios', methods=['POST'])
def admin_criar_bloqueio():
    """Cria um novo bloqueio."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados são obrigatórios.'}), 400

    data = dados.get('data', '')
    data_fim = dados.get('dataFim', '')
    hora_inicio = dados.get('horaInicio', '')
    hora_fim = dados.get('horaFim', '')
    motivo = dados.get('motivo', '').strip()

    if not data:
        return jsonify({'erro': 'Data é obrigatória.'}), 400

    bl_id = gerar_id()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO bloqueios (id, data, data_fim, hora_inicio, hora_fim, motivo) VALUES (%s, %s, %s, %s, %s, %s)',
        (bl_id, data, data_fim, hora_inicio, hora_fim, motivo)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'bloqueio': {'id': bl_id}}), 201


@app.route('/api/admin/bloqueios/<bl_id>', methods=['DELETE'])
def admin_remover_bloqueio(bl_id):
    """Remove um bloqueio."""
    if not verificar_admin():
        return jsonify({'erro': 'Não autorizado.'}), 401

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bloqueios WHERE id = %s', (bl_id,))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Bloqueio não encontrado.'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


# ===================== INICIALIZAÇÃO =====================

# Inicializar banco ao importar (para gunicorn)
print('[INFO] Inicializando banco de dados...')
init_db()
seed_default_data()
print('[OK] Sistema BarbeCity Jaraguá iniciado!')

if __name__ == '__main__':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    print(f'[OK] Servidor rodando em http://0.0.0.0:{port}')
    print(f'[OK] Painel admin: http://localhost:{port}/admin')
    print(f'[OK] Agendamento: http://localhost:{port}/agendamento')
    app.run(host='0.0.0.0', port=port, debug=debug)
