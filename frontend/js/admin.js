/**
 * admin.js — Lógica completa do Painel Administrativo
 * ====================================================
 * Login, dashboard, CRUD de agendamentos, serviços e bloqueios.
 */

let periodoAtual = 'hoje';

document.addEventListener('DOMContentLoaded', async () => {
    const savedSecret = localStorage.getItem('admin_secret');
    if (savedSecret) {
        // Validar se a senha salva ainda funciona
        try {
            await adminFinanceiro('hoje');
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('dashboard-screen').classList.remove('hidden');
            carregarDashboard();
        } catch (err) {
            // Senha inválida, limpar e mostrar login
            localStorage.removeItem('admin_secret');
        }
    }
});

async function fazerLogin(event) {
    event.preventDefault();
    const senha = document.getElementById('admin-password').value.trim();

    if (!senha) {
        mostrarToast('Digite a senha.', 'error');
        return;
    }

    setAdminSecret(senha);

    // Testar se a senha está correta antes de mostrar o dashboard
    try {
        await adminFinanceiro('hoje');
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        document.getElementById('admin-password').value = '';
        carregarDashboard();
        mostrarToast('✅ Login realizado!', 'success');
    } catch (err) {
        localStorage.removeItem('admin_secret');
        mostrarToast('❌ Senha incorreta!', 'error');
    }
}

function sairAdmin() {
    localStorage.removeItem('admin_secret');
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('dashboard-screen').classList.add('hidden');
}

// ===================== DASHBOARD =====================

async function carregarDashboard() {
    await Promise.all([
        carregarStats(),
        carregarAgendamentos(),
        carregarServicos(),
        carregarBloqueios()
    ]);
}

function filtrarPeriodo(periodo) {
    periodoAtual = periodo;

    // Atualizar botões
    ['hoje', 'semana', 'mes', 'todos'].forEach(p => {
        const btn = document.getElementById(`filtro-${p}`);
        if (btn) {
            btn.className = p === periodo ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary';
        }
    });

    carregarStats();
    carregarAgendamentos();
}

async function carregarStats() {
    try {
        const data = await adminFinanceiro(periodoAtual);
        const container = document.getElementById('stats-container');

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-value">${formatarMoeda(data.faturamentoLiquido || 0)}</div>
                <div class="stat-label">Faturamento Líquido</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">${formatarMoeda(data.faturamentoBruto || 0)}</div>
                <div class="stat-label">Faturamento Bruto</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-value">${data.concluidos || 0}</div>
                <div class="stat-label">Concluídos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📅</div>
                <div class="stat-value">${data.agendados || 0}</div>
                <div class="stat-label">Agendados</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">❌</div>
                <div class="stat-value">${data.cancelados || 0}</div>
                <div class="stat-label">Cancelados</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👤</div>
                <div class="stat-value">${data.ausentes || 0}</div>
                <div class="stat-label">Ausentes</div>
            </div>
        `;
    } catch (err) {
        document.getElementById('stats-container').innerHTML =
            `<p class="text-danger">Erro: ${err.message}</p>`;
    }
}

async function carregarAgendamentos() {
    try {
        const data = await adminListarAgendamentos(periodoAtual);
        const container = document.getElementById('agendamentos-table');
        const countEl = document.getElementById('agendamentos-count');

        if (data.agendamentos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <p>Nenhum agendamento neste período.</p>
                </div>
            `;
            countEl.textContent = '0 agendamentos';
            return;
        }

        countEl.textContent = `${data.agendamentos.length} agendamento(s)`;

        let html = `<table>
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Horário</th>
                    <th>Cliente</th>
                    <th>Serviço</th>
                    <th>Valor</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>`;

        data.agendamentos.forEach(ag => {
            const dataBr = formatarDataBR(ag.data_hora_inicio);
            const hora = formatarHora(ag.data_hora_inicio);
            const statusClass = getStatusBadge(ag.status);
            const statusLabel = getStatusLabel(ag.status);

            html += `
                <tr>
                    <td>${dataBr}</td>
                    <td><strong>${hora}</strong></td>
                    <td>${ag.cliente_nome}</td>
                    <td>${ag.servico_nome}</td>
                    <td>${formatarMoeda(ag.valor_original)}</td>
                    <td><span class="badge ${statusClass}">${statusLabel}</span></td>
                    <td>
                        ${ag.status === 'agendado' ? `<button class="btn btn-sm btn-success" onclick="confirmarAtendimento('${ag.id}')" title="Confirmar atendimento">
                            ✅
                        </button>` : ''}
                        <button class="btn btn-sm btn-secondary" onclick="abrirEditarAgendamento('${ag.id}', '${ag.status}', ${ag.valor_pago || 0})">
                            ✏️
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="cancelarAgendamento('${ag.id}')">
                            🗑️
                        </button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (err) {
        document.getElementById('agendamentos-table').innerHTML =
            `<p class="text-danger">Erro: ${err.message}</p>`;
    }
}

// ===================== CRUD AGENDAMENTOS =====================

function abrirEditarAgendamento(id, status, valorPago) {
    document.getElementById('edit-ag-id').value = id;
    document.getElementById('edit-status').value = status;
    document.getElementById('edit-valor').value = valorPago || 0;
    abrirModal('modal-editar-agendamento');
}

async function salvarEdicaoAgendamento(event) {
    event.preventDefault();
    const id = document.getElementById('edit-ag-id').value;
    const status = document.getElementById('edit-status').value;
    const valor = parseFloat(document.getElementById('edit-valor').value) || 0;

    try {
        await adminAtualizarAgendamento(id, { status, valorPago: valor });
        mostrarToast('✅ Agendamento atualizado!', 'success');
        fecharModal('modal-editar-agendamento');
        carregarAgendamentos();
        carregarStats();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function confirmarAtendimento(id) {
    if (!confirm('Confirmar que este atendimento foi realizado?')) return;

    try {
        await adminAtualizarAgendamento(id, { status: 'concluido' });
        mostrarToast('✅ Atendimento confirmado!', 'success');
        carregarAgendamentos();
        carregarStats();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function cancelarAgendamento(id) {
    if (!confirm('Tem certeza que deseja cancelar este agendamento?')) return;

    try {
        await adminCancelarAgendamento(id);
        mostrarToast('✅ Agendamento cancelado!', 'success');
        carregarDashboard();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function limparCancelados() {
    if (!confirm('Deseja remover PERMANENTEMENTE todos os agendamentos cancelados? Esta ação não pode ser desfeita.')) return;

    try {
        const result = await adminLimparCancelados();
        mostrarToast(`✅ ${result.removidos} agendamentos removidos!`, 'success');
        carregarDashboard();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

// ===================== CRUD SERVIÇOS =====================

async function carregarServicos() {
    try {
        const data = await adminListarServicos();
        const container = document.getElementById('servicos-table');

        if (data.servicos.length === 0) {
            container.innerHTML = '<p class="text-secondary">Nenhum serviço cadastrado.</p>';
            return;
        }

        let html = `<table>
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>Duração</th>
                    <th>Valor</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>`;

        data.servicos.forEach(s => {
            const sJson = JSON.stringify(s).replace(/"/g, '&quot;');
            html += `
                <tr>
                    <td>${s.nome}</td>
                    <td>${s.duracao_minutos} min</td>
                    <td>${formatarMoeda(s.valor)}</td>
                    <td>${s.ativo ? '✅ Ativo' : '❌ Inativo'}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="abrirEditarServico('${sJson}')">✏️</button>
                        ${s.ativo ? `<button class="btn btn-sm btn-danger" onclick="desativarServico(${s.id})">Desativar</button>` : ''}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (err) {
        document.getElementById('servicos-table').innerHTML =
            `<p class="text-danger">Erro: ${err.message}</p>`;
    }
}

function abrirModalServico() {
    document.getElementById('form-novo-servico').reset();
    document.getElementById('edit-servico-id').value = '';
    document.getElementById('modal-servico-titulo').textContent = 'Novo Serviço';
    document.getElementById('btn-salvar-servico').textContent = 'Criar Serviço';
    abrirModal('modal-novo-servico');
}

function abrirEditarServico(sJson) {
    const s = JSON.parse(sJson);
    document.getElementById('edit-servico-id').value = s.id;
    document.getElementById('novo-servico-nome').value = s.nome;
    document.getElementById('novo-servico-desc').value = s.descricao || '';
    document.getElementById('novo-servico-duracao').value = s.duracao_minutos;
    document.getElementById('novo-servico-valor').value = s.valor;
    
    document.getElementById('modal-servico-titulo').textContent = 'Editar Serviço';
    document.getElementById('btn-salvar-servico').textContent = 'Salvar Alterações';
    abrirModal('modal-novo-servico');
}

async function salvarServico(event) {
    event.preventDefault();

    const id = document.getElementById('edit-servico-id').value;
    const nome = document.getElementById('novo-servico-nome').value.trim();
    const descricao = document.getElementById('novo-servico-desc').value.trim();
    const duracao = parseInt(document.getElementById('novo-servico-duracao').value);
    const valor = parseFloat(document.getElementById('novo-servico-valor').value);

    if (!nome || !duracao || !valor) {
        mostrarToast('Preencha todos os campos obrigatórios.', 'error');
        return;
    }

    try {
        if (id) {
            await adminAtualizarServico(id, { nome, descricao, duracaoMinutos: duracao, valor });
            mostrarToast('✅ Serviço atualizado!', 'success');
        } else {
            await adminCriarServico({ nome, descricao, duracaoMinutos: duracao, valor });
            mostrarToast('✅ Serviço criado!', 'success');
        }
        fecharModal('modal-novo-servico');
        carregarServicos();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function desativarServico(id) {
    if (!confirm('Desativar este serviço?')) return;

    try {
        await adminDesativarServico(id);
        mostrarToast('✅ Serviço desativado!', 'success');
        carregarServicos();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

// ===================== CRUD BLOQUEIOS =====================

async function carregarBloqueios() {
    try {
        const data = await adminListarBloqueios();
        const container = document.getElementById('bloqueios-list');

        if (data.bloqueios.length === 0) {
            container.innerHTML = '<p class="text-secondary">Nenhum bloqueio cadastrado.</p>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 0.5rem;">';

        data.bloqueios.forEach(b => {
            const dataBr = formatarDataBR(b.data);
            const dataFimBr = b.data_fim ? formatarDataBR(b.data_fim) : '';
            const intervaloData = dataFimBr ? `${dataBr} até ${dataFimBr}` : dataBr;
            
            const horario = b.hora_inicio && b.hora_fim
                ? `${b.hora_inicio} às ${b.hora_fim}`
                : 'Dia inteiro';

            html += `
                <div class="flex items-center justify-between" style="background: var(--bg-tertiary); padding: 0.75rem 1rem; border-radius: var(--radius);">
                    <div>
                        <strong>${intervaloData}</strong> — ${horario}
                        ${b.motivo ? `<br><span class="text-secondary">${b.motivo}</span>` : ''}
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="removerBloqueio('${b.id}')">✕</button>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch (err) {
        document.getElementById('bloqueios-list').innerHTML =
            `<p class="text-danger">Erro: ${err.message}</p>`;
    }
}

function abrirModalBloqueio() {
    document.getElementById('form-bloqueio').reset();
    document.getElementById('bloqueio-data').value = new Date().toISOString().split('T')[0];
    abrirModal('modal-bloqueio');
}

async function criarBloqueio(event) {
    event.preventDefault();

    const data = document.getElementById('bloqueio-data').value;
    const horaInicio = document.getElementById('bloqueio-hora-inicio').value;
    const horaFim = document.getElementById('bloqueio-hora-fim').value;
    const motivo = document.getElementById('bloqueio-motivo').value.trim();

    if (!data) {
        mostrarToast('Selecione uma data.', 'error');
        return;
    }

    try {
        await adminCriarBloqueio({ data, horaInicio, horaFim, motivo });
        mostrarToast('✅ Data bloqueada!', 'success');
        fecharModal('modal-bloqueio');
        carregarBloqueios();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function removerBloqueio(id) {
    if (!confirm('Remover este bloqueio?')) return;

    try {
        await adminRemoverBloqueio(id);
        mostrarToast('✅ Bloqueio removido!', 'success');
        carregarBloqueios();
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

// ===================== MODAIS =====================

function abrirModal(id) {
    document.getElementById(id).classList.add('active');
}

function fecharModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Fechar modal ao clicar fora
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});
