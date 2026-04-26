"""
services.py — Regras de Negócio
================================
Algoritmo de cálculo de slots disponíveis, validações e lógica financeira.
"""

from datetime import datetime, timedelta, date, time
from typing import Optional
import uuid
import hashlib
import secrets


def gerar_hash_id() -> str:
    """Gera um hash ID único de 10 caracteres para identificação do agendamento."""
    return secrets.token_hex(5)[:10]


def gerar_id() -> str:
    """Gera um UUID para o ID do agendamento."""
    return str(uuid.uuid4())


def time_to_minutes(t: str) -> int:
    """Converte string 'HH:MM' para minutos desde meia-noite."""
    if not t or ':' not in t:
        return 0
    h, m = t.split(':')
    return int(h) * 60 + int(m)


def minutes_to_time(minutes: int) -> str:
    """Converte minutos desde meia-noite para string 'HH:MM'."""
    h = minutes // 60
    m = minutes % 60
    return f'{h:02d}:{m:02d}'


def formatar_data_br(data_str) -> str:
    """Converte ISO date para DD/MM. Aceita string ISO ou objeto datetime."""
    try:
        if isinstance(data_str, datetime):
            d = data_str
        else:
            d = datetime.fromisoformat(str(data_str))
        return d.strftime('%d/%m')
    except:
        return str(data_str)


def formatar_hora_br(data_str) -> str:
    """Extrai HH:MM de uma string ISO datetime. Aceita string ISO ou objeto datetime."""
    try:
        if isinstance(data_str, datetime):
            d = data_str
        else:
            d = datetime.fromisoformat(str(data_str))
        return d.strftime('%H:%M')
    except:
        return str(data_str)



def calcular_slots_disponiveis(
    data: str,
    servico_id: int,
    servico_duracao: int,
    servico_buffer: int,
    config_horario: dict,
    agendamentos_existentes: list,
    bloqueios: list
) -> list:
    """
    Calcula os slots disponíveis para uma determinada data e serviço.

    Args:
        data: Data no formato 'YYYY-MM-DD'
        servico_id: ID do serviço
        servico_duracao: Duração do serviço em minutos
        servico_buffer: Buffer entre agendamentos em minutos
        config_horario: Dict com 'abertura', 'fechamento', 'ativo'
        agendamentos_existentes: Lista de agendamentos já marcados
        bloqueios: Lista de bloqueios para a data

    Returns:
        Lista de slots disponíveis
    """
    if not config_horario or not config_horario.get('ativo'):
        return []

    abertura = config_horario['abertura']
    fechamento = config_horario['fechamento']
    buffer = config_horario.get('intervalo_corte_minutos', servico_buffer)

    # Duração total do slot = duração do serviço + buffer
    duracao_total = servico_duracao + buffer

    abertura_min = time_to_minutes(abertura)
    fechamento_min = time_to_minutes(fechamento)

    # O último slot deve terminar até o fechamento
    ultimo_inicio_valido = fechamento_min - servico_duracao

    slots = []

    # Gerar slots brutos
    hora_atual = abertura_min
    while hora_atual <= ultimo_inicio_valido:
        hora_fim = hora_atual + duracao_total
        if hora_fim > fechamento_min:
            break

        slot_inicio = minutes_to_time(hora_atual)
        slot_fim = minutes_to_time(hora_fim)

        slots.append({
            'horaInicio': slot_inicio,
            'horaFim': slot_fim,
            'disponivel': True,
            'servicoId': servico_id
        })

        hora_atual += duracao_total

    # Remover slots conflitantes com agendamentos existentes
    for ag in agendamentos_existentes:
        if ag['status'] in ('cancelado',):
            continue
        ag_inicio = formatar_hora_br(ag['data_hora_inicio'])
        ag_fim = formatar_hora_br(ag['data_hora_fim'])

        ag_inicio_min = time_to_minutes(ag_inicio)
        ag_fim_min = time_to_minutes(ag_fim)

        slots = [
            s for s in slots
            if not (
                time_to_minutes(s['horaInicio']) < ag_fim_min and
                time_to_minutes(s['horaFim']) > ag_inicio_min
            )
        ]

    # Remover slots em horários bloqueados
    for bl in bloqueios:
        if bl.get('hora_inicio') and bl.get('hora_fim'):
            bl_inicio_min = time_to_minutes(bl['hora_inicio'])
            bl_fim_min = time_to_minutes(bl['hora_fim'])
            slots = [
                s for s in slots
                if not (
                    time_to_minutes(s['horaInicio']) < bl_fim_min and
                    time_to_minutes(s['horaFim']) > bl_inicio_min
                )
            ]
        else:
            # Bloqueio de dia inteiro
            return []

    return slots


def validar_agendamento(
    cliente_nome: str,
    data_hora_inicio: str,
    servico_id: int,
    servico_duracao: int,
    servico_buffer: int,
    config_horario: dict,
    agendamentos_conflitantes: list,
    bloqueios: list
) -> dict:
    """
    Valida se um agendamento pode ser realizado.

    Returns:
        Dict com 'valido' (bool) e 'erro' (str opcional)
    """
    if not cliente_nome or not cliente_nome.strip():
        return {'valido': False, 'erro': 'Nome do cliente é obrigatório.'}

    if not data_hora_inicio:
        return {'valido': False, 'erro': 'Data e horário são obrigatórios.'}

    if not servico_id:
        return {'valido': False, 'erro': 'Serviço é obrigatório.'}

    # Validar horário de funcionamento
    if not config_horario or not config_horario.get('ativo'):
        return {'valido': False, 'erro': 'A barbearia está fechada neste dia.'}

    # Validar horário mínimo (30 min a partir de agora)
    try:
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        agora = datetime.now(dt_inicio.tzinfo) if dt_inicio.tzinfo else datetime.now()
        if dt_inicio < agora + timedelta(minutes=30):
            return {'valido': False, 'erro': 'O agendamento deve ser com pelo menos 30 minutos de antecedência.'}
    except:
        return {'valido': False, 'erro': 'Formato de data/hora inválido.'}

    # Validar conflito com agendamentos existentes
    if agendamentos_conflitantes and len(agendamentos_conflitantes) > 0:
        return {'valido': False, 'erro': 'Este horário não está mais disponível.'}

    # Validar bloqueios
    for bl in bloqueios:
        if bl.get('hora_inicio') and bl.get('hora_fim'):
            hora_inicio = formatar_hora_br(data_hora_inicio)
            if (time_to_minutes(hora_inicio) >= time_to_minutes(bl['hora_inicio']) and
                time_to_minutes(hora_inicio) < time_to_minutes(bl['hora_fim'])):
                return {'valido': False, 'erro': 'Horário bloqueado. Tente outro dia/horário.'}
        else:
            return {'valido': False, 'erro': 'Dia bloqueado. Tente outra data.'}

    return {'valido': True}


def calcular_resumo_financeiro(agendamentos: list) -> dict:
    """
    Calcula o resumo financeiro a partir de uma lista de agendamentos.
    """
    total_bruto = 0.0
    total_liquido = 0.0
    cancelados = 0
    ausentes = 0
    concluidos = 0
    agendados = 0

    for ag in agendamentos:
        if ag['status'] == 'concluido':
            total_bruto += ag['valor_original']
            total_liquido += ag['valor_pago'] if ag['valor_pago'] else ag['valor_original']
            concluidos += 1
        elif ag['status'] == 'cancelado':
            cancelados += 1
        elif ag['status'] == 'ausente':
            ausentes += 1
        elif ag['status'] == 'agendado':
            agendados += 1

    return {
        'faturamentoBruto': round(total_bruto, 2),
        'faturamentoLiquido': round(total_liquido, 2),
        'cancelados': cancelados,
        'ausentes': ausentes,
        'concluidos': concluidos,
        'agendados': agendados,
        'totalAtendimentos': concluidos + cancelados + ausentes
    }


def formatar_mensagem_whatsapp(
    cliente_nome: str,
    data: str,
    hora_inicio: str,
    hora_fim: str,
    servico_nome: str,
    valor: float,
    nota_opcional: str,
    url_site: str
) -> str:
    """
    Formata a mensagem para envio via WhatsApp conforme RF6.
    """
    nota = nota_opcional if nota_opcional.strip() else '—'

    mensagem = (
        f"✂️ *Novo Agendamento — Barbearia*\n"
        f"──────────────────────────\n"
        f"👤 *Cliente:* {cliente_nome}\n"
        f"📅 *Data:* {data}\n"
        f"⏰ *Horário:* {hora_inicio} às {hora_fim}\n"
        f"💇‍♂️ *Serviço:* {servico_nome}\n"
        f"💰 *Valor:* R$ {valor:.2f}\n"
        f"📝 *Observações:* {nota}\n"
        f"──────────────────────────\n"
        f"🔗 Acesse o site: {url_site}"
    )

    return mensagem
