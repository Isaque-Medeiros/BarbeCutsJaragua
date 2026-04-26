/**
 * api.js — Cliente HTTP para comunicação com o backend Flask
 * ==========================================================
 * Funções auxiliares para chamar todos os endpoints da API.
 */

const API_BASE = '';

const ADMIN_SECRET = localStorage.getItem('admin_secret') || '';

function setAdminSecret(secret) {
    localStorage.setItem('admin_secret', secret);
}

function getAdminHeaders() {
    const secret = localStorage.getItem('admin_secret');
    if (secret) {
        return { 'x-admin-secret': secret, 'Content-Type': 'application/json' };
    }
    return { 'Content-Type': 'application/json' };
}

async function apiGet(endpoint, admin = false) {
    const headers = admin ? getAdminHeaders() : {};
    const response = await fetch(`${API_BASE}${endpoint}`, { headers });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ erro: 'Erro na requisição' }));
        throw new Error(error.erro || `Erro ${response.status}`);
    }
    return response.json();
}

async function apiPost(endpoint, data, admin = false) {
    const headers = admin ? getAdminHeaders() : { 'Content-Type': 'application/json' };
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ erro: 'Erro na requisição' }));
        throw new Error(error.erro || `Erro ${response.status}`);
    }
    return response.json();
}

async function apiPut(endpoint, data) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: getAdminHeaders(),
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ erro: 'Erro na requisição' }));
        throw new Error(error.erro || `Erro ${response.status}`);
    }
    return response.json();
}

async function apiDelete(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE',
        headers: getAdminHeaders()
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ erro: 'Erro na requisição' }));
        throw new Error(error.erro || `Erro ${response.status}`);
    }
    return response.json();
}

// ===================== Funções Específicas =====================

async function listarServicos() {
    return apiGet('/api/servicos');
}

async function buscarHorarios(data, servicoId) {
    return apiGet(`/api/horarios?data=${data}&servicoId=${servicoId}`);
}

async function criarAgendamento(dados) {
    return apiPost('/api/agendamentos', dados);
}

async function consultarAgendamento(hash) {
    return apiGet(`/api/agendamentos/consulta?hash=${hash}`);
}

async function getConfigHorarios() {
    return apiGet('/api/config/horarios');
}

// Admin
async function adminListarAgendamentos(periodo = 'hoje', dataInicio = '', dataFim = '') {
    let url = `/api/admin/agendamentos?periodo=${periodo}`;
    if (dataInicio) url += `&dataInicio=${dataInicio}`;
    if (dataFim) url += `&dataFim=${dataFim}`;
    return apiGet(url, true);
}

async function adminFinanceiro(periodo = 'hoje', dataInicio = '', dataFim = '') {
    let url = `/api/admin/financeiro?periodo=${periodo}`;
    if (dataInicio) url += `&dataInicio=${dataInicio}`;
    if (dataFim) url += `&dataFim=${dataFim}`;
    return apiGet(url, true);
}

async function adminAtualizarAgendamento(id, dados) {
    return apiPut(`/api/admin/agendamentos/${id}`, dados);
}

async function adminCancelarAgendamento(id) {
    return apiDelete(`/api/admin/agendamentos/${id}`);
}

async function adminListarServicos() {
    return apiGet('/api/admin/servicos', true);
}

async function adminCriarServico(dados) {
    return apiPost('/api/admin/servicos', dados, true);
}

async function adminAtualizarServico(id, dados) {
    return apiPut(`/api/admin/servicos/${id}`, dados);
}

async function adminDesativarServico(id) {
    return apiDelete(`/api/admin/servicos/${id}`);
}

async function adminListarBloqueios() {
    return apiGet('/api/admin/bloqueios', true);
}

async function adminCriarBloqueio(dados) {
    return apiPost('/api/admin/bloqueios', dados, true);
}

async function adminRemoverBloqueio(id) {
    return apiDelete(`/api/admin/bloqueios/${id}`);
}

// ===================== Utilitários =====================

function formatarDataISO(data) {
    const d = new Date(data);
    return d.toISOString().split('T')[0];
}

function formatarDataBR(dataISO) {
    // dataISO pode vir como "2026-04-26" ou "2026-04-26T14:00:00"
    if (!dataISO) return '—';
    // Extrair apenas a parte da data (YYYY-MM-DD)
    const parteData = dataISO.split('T')[0];
    const partes = parteData.split('-');
    if (partes.length < 3) return dataISO;
    // Formato brasileiro: DD/MM/AAAA
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

function formatarDataBRCurta(dataISO) {
    // Apenas DD/MM (para exibição compacta)
    if (!dataISO) return '—';
    const parteData = dataISO.split('T')[0];
    const partes = parteData.split('-');
    if (partes.length < 3) return dataISO;
    return `${partes[2]}/${partes[1]}`;
}

function formatarHora(dataISO) {
    // dataISO pode vir como "2026-04-26T14:00:00" ou "2026-04-26T14:50:00"
    if (!dataISO) return '—';
    // Extrair apenas a parte da hora (HH:MM)
    const parteHora = dataISO.split('T')[1];
    if (!parteHora) return dataISO;
    return parteHora.substring(0, 5);
}


function getDiaSemanaNome(dia) {
    const dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
    return dias[dia] || '';
}

function getStatusBadge(status) {
    const map = {
        'agendado': 'badge-agendado',
        'concluido': 'badge-concluido',
        'cancelado': 'badge-cancelado',
        'ausente': 'badge-ausente'
    };
    return map[status] || 'badge-agendado';
}

function getStatusLabel(status) {
    const map = {
        'agendado': 'Agendado',
        'concluido': 'Concluído',
        'cancelado': 'Cancelado',
        'ausente': 'Ausente'
    };
    return map[status] || status;
}

function mostrarToast(mensagem, tipo = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensagem;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function mostrarLoading(container) {
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

function formatarMoeda(valor) {
    return `R$ ${parseFloat(valor).toFixed(2)}`;
}
