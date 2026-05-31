/**
 * agendamento.js — Lógica completa da página de agendamento
 * ==========================================================
 * Gerencia as 4 etapas: Serviço → Data/Horário → Dados → WhatsApp Obrigatório → Ticket
 * Tema: BarbeCity Jaraguá
 */

let servicos = [];
let servicosAdicionais = [];
let servicoSelecionado = null;
let adicionaisSelecionados = [];
let dataSelecionada = null;
let slotSelecionado = null;
let ultimoAgendamento = null;
let slotsDisponiveis = [];
let aguardandoWhatsApp = false;

document.addEventListener('DOMContentLoaded', async () => {
    await carregarServicos();
    gerarDiasDisponiveis();
    setupHamburger();

    const form = document.getElementById('agendamento-form');
    if (form) {
        form.addEventListener('submit', confirmarAgendamento);
    }

    const telefoneInput = document.getElementById('telefoneContato');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', formatarTelefone);
    }

    // Input de horário personalizado
    const horarioInput = document.getElementById('horario-personalizado');
    if (horarioInput) {
        horarioInput.addEventListener('input', validarHorarioPersonalizado);
        horarioInput.addEventListener('blur', validarHorarioPersonalizado);
    }
});

// ===================== HAMBURGER MENU =====================

function setupHamburger() {
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-overlay');
    if (!hamburger) return;
    function toggleMenu() {
        hamburger.classList.toggle('active');
        mobileMenu.classList.toggle('open');
        overlay.classList.toggle('open');
        document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
    }
    hamburger.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', toggleMenu);
    });
}

// ===================== FORMATAÇÃO DE TELEFONE =====================

function formatarTelefone(e) {
    let valor = e.target.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.slice(0, 11);
    if (valor.length > 7) {
        valor = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7)}`;
    } else if (valor.length > 2) {
        valor = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
    } else if (valor.length > 0) {
        valor = `(${valor}`;
    }
    e.target.value = valor;
}

// ===================== STEP 1: SERVIÇOS =====================

async function carregarServicos() {
    try {
        const data = await listarServicos();
        const cortes = data.servicos.filter(s => s.tipo === 'principal');
        servicosAdicionais = data.servicos.filter(s => s.tipo === 'adicional');
        const combos = data.servicos.filter(s => s.tipo === 'combo');
        servicos = [...cortes, ...combos];

        const container = document.getElementById('servicos-selecao');
        container.innerHTML = '';

        if (servicos.length === 0 && servicosAdicionais.length === 0) {
            container.innerHTML = '<p class="text-secondary" style="text-align: center;">Nenhum serviço disponível.</p>';
            return;
        }

        if (cortes.length > 0) {
            const secao = document.createElement('div');
            secao.className = 'secao-servicos';
            secao.innerHTML = '<h3 class="secao-titulo">✂️ Cortes</h3><div class="grid grid-servicos"></div>';
            const grid = secao.querySelector('.grid');
            cortes.forEach(s => grid.appendChild(criarCardServico(s)));
            container.appendChild(secao);
        }

        if (servicosAdicionais.length > 0) {
            const secao = document.createElement('div');
            secao.className = 'secao-servicos';
            secao.innerHTML = '<h3 class="secao-titulo">✨ Adicionais</h3><div class="grid grid-servicos"></div>';
            const grid = secao.querySelector('.grid');
            servicosAdicionais.forEach(s => grid.appendChild(criarCardServico(s)));
            container.appendChild(secao);
        }

        if (combos.length > 0) {
            const secao = document.createElement('div');
            secao.className = 'secao-servicos';
            secao.innerHTML = '<h3 class="secao-titulo">🔥 Combos</h3><div class="grid grid-servicos"></div>';
            const grid = secao.querySelector('.grid');
            combos.forEach(s => grid.appendChild(criarCardServico(s)));
            container.appendChild(secao);
        }
    } catch (err) {
        document.getElementById('servicos-selecao').innerHTML =
            `<p class="text-danger" style="text-align: center;">Erro: ${err.message}</p>`;
    }
}

function criarCardServico(s) {
    const card = document.createElement('div');
    card.className = 'service-card';
    card.dataset.id = s.id;
    card.onclick = () => selecionarServico(s.id);
    const icone = getIconeServico(s);
    card.innerHTML = `
        <div class="service-icon">${icone}</div>
        <div class="service-name">${s.nome}</div>
        <div class="service-desc">${s.descricao || 'Serviço profissional'}</div>
        <div class="service-footer">
            <span class="service-price">R$ ${parseFloat(s.valor).toFixed(2)}</span>
            <span class="service-duration">⏱ ${s.duracao_minutos} min</span>
        </div>
    `;
    return card;
}

function getIconeServico(s) {
    const nomeLower = s.nome.toLowerCase();
    if (s.tipo === 'combo') return '🔥';
    if (s.tipo === 'adicional') {
        if (nomeLower.includes('botox')) return '💉';
        if (nomeLower.includes('luzes')) return '💡';
        return '✨';
    }
    if (nomeLower.includes('corte')) return '✂️';
    if (nomeLower.includes('barba')) return '🪒';
    if (nomeLower.includes('sobrancelha')) return '✨';
    return '✂️';
}

function selecionarServico(id) {
    const servicoAdd = servicosAdicionais.find(s => s.id === id);
    servicoSelecionado = servicoAdd || servicos.find(s => s.id === id);
    if (!servicoSelecionado) return;

    document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
    const card = document.querySelector(`.service-card[data-id="${id}"]`);
    if (card) card.classList.add('selected');

    irParaStep(2);
    carregarSlots();
    renderizarAdicionais();
}

function renderizarAdicionais() {
    const container = document.getElementById('adicionais-container');
    if (!container) return;
    container.innerHTML = '';

    let adicionaisDisponiveis = [...servicosAdicionais];
    if (servicoSelecionado && servicoSelecionado.tipo === 'adicional') {
        adicionaisDisponiveis = adicionaisDisponiveis.filter(s => s.id !== servicoSelecionado.id);
    }

    if (adicionaisDisponiveis.length === 0) {
        container.innerHTML = '<p class="text-secondary" style="font-size: 0.9rem;">Nenhum adicional disponível.</p>';
        return;
    }

    adicionaisDisponiveis.forEach(s => {
        const card = document.createElement('div');
        card.className = 'service-card service-card-sm';
        card.dataset.id = s.id;
        if (adicionaisSelecionados.includes(s.id)) card.classList.add('selected');
        card.onclick = () => toggleAdicional(s.id);
        let icone = s.nome.toLowerCase().includes('botox') ? '💉' : '💡';
        card.innerHTML = `
            <div class="service-icon" style="font-size: 1.2rem;">${icone}</div>
            <div class="service-name" style="font-size: 0.9rem;">${s.nome}</div>
            <div class="service-footer">
                <span class="service-price" style="font-size: 0.85rem;">R$ ${parseFloat(s.valor).toFixed(2)}</span>
                <span class="service-duration" style="font-size: 0.75rem;">⏱ ${s.duracao_minutos} min</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function toggleAdicional(id) {
    const index = adicionaisSelecionados.indexOf(id);
    if (index === -1) adicionaisSelecionados.push(id);
    else adicionaisSelecionados.splice(index, 1);
    document.querySelectorAll('#adicionais-container .service-card').forEach(c => {
        c.classList.toggle('selected', adicionaisSelecionados.includes(parseInt(c.dataset.id)));
    });
}

// ===================== STEP 2: DATA E HORÁRIO =====================

function gerarDiasDisponiveis() {
    const container = document.getElementById('dias-container');
    container.innerHTML = '';
    const hoje = new Date();
    const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    for (let i = 0; i < 14; i++) {
        const data = new Date(hoje);
        data.setDate(hoje.getDate() + i);
        const year = data.getFullYear();
        const month = String(data.getMonth() + 1).padStart(2, '0');
        const day = String(data.getDate()).padStart(2, '0');
        const dataStr = `${year}-${month}-${day}`;
        const diaSemana = data.getDay();
        const diaMes = data.getDate();
        const mes = data.getMonth() + 1;

        const btn = document.createElement('button');
        btn.className = 'date-btn';
        btn.dataset.data = dataStr;
        btn.innerHTML = `<span class="date-day">${diasSemana[diaSemana]}</span><span class="date-num">${diaMes}/${mes}</span>`;
        btn.onclick = () => selecionarData(dataStr);
        container.appendChild(btn);
    }
}

function selecionarData(dataStr) {
    dataSelecionada = dataStr;
    document.querySelectorAll('.date-btn').forEach(b => {
        b.classList.remove('selected');
        if (b.dataset.data === dataStr) b.classList.add('selected');
    });
    carregarSlots();
}

async function carregarSlots() {
    if (!servicoSelecionado || !dataSelecionada) return;
    const container = document.getElementById('slots-container');
    mostrarLoading(container);

    try {
        const data = await buscarHorarios(dataSelecionada, servicoSelecionado.id);
        slotsDisponiveis = data.slotsDisponiveis || [];

        if (slotsDisponiveis.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <p>Nenhum horário disponível para esta data.</p>
                    <p class="text-secondary" style="font-size: 0.85rem;">Tente outro dia.</p>
                </div>
            `;
            return;
        }

        let html = '<label class="form-label">Horários disponíveis:</label>';
        
        // Input de horário personalizado
        html += `
            <div class="horario-personalizado-wrapper">
                <input type="text" id="horario-personalizado" class="form-input" 
                       placeholder="Digite um horário específico (ex: 14:25)" maxlength="5">
                <div id="horario-personalizado-status" class="form-hint"></div>
            </div>
        `;
        
        html += '<div class="slots-grid">';
        slotsDisponiveis.forEach(s => {
            html += `<button class="slot-btn" onclick="selecionarSlot('${s.horaInicio}', '${s.horaFim}')">${s.horaInicio}</button>`;
        });
        html += '</div>';
        container.innerHTML = html;

        // Re-adicionar event listener ao input personalizado
        const horarioInput = document.getElementById('horario-personalizado');
        if (horarioInput) {
            horarioInput.addEventListener('input', validarHorarioPersonalizado);
            horarioInput.addEventListener('blur', validarHorarioPersonalizado);
        }

    } catch (err) {
        container.innerHTML = `<p class="text-danger">Erro ao carregar horários: ${err.message}</p>`;
    }
}

function validarHorarioPersonalizado() {
    const input = document.getElementById('horario-personalizado');
    const status = document.getElementById('horario-personalizado-status');
    if (!input || !status) return;

    let valor = input.value.replace(/[^0-9:]/g, '');
    
    // Auto-adicionar : após 2 dígitos
    if (valor.length === 2 && !valor.includes(':')) {
        valor = valor + ':';
    }
    if (valor.length > 5) valor = valor.slice(0, 5);
    input.value = valor;

    if (valor.length < 5) {
        status.textContent = 'Digite um horário no formato HH:MM';
        status.className = 'form-hint';
        input.classList.remove('error', 'success');
        return;
    }

    const [h, m] = valor.split(':');
    const hora = parseInt(h);
    const min = parseInt(m);

    if (isNaN(hora) || isNaN(min) || hora < 0 || hora > 23 || min < 0 || min > 59) {
        status.textContent = '❌ Horário inválido. Use formato HH:MM (ex: 14:30)';
        status.className = 'form-hint text-danger';
        input.classList.add('error');
        input.classList.remove('success');
        return;
    }

    // Verificar se o horário está disponível
    const horarioStr = `${String(hora).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
    const slotEncontrado = slotsDisponiveis.find(s => s.horaInicio === horarioStr);

    if (slotEncontrado) {
        status.textContent = '✅ Horário disponível! Clique para selecionar.';
        status.className = 'form-hint text-success';
        input.classList.add('success');
        input.classList.remove('error');
        
        // Auto-selecionar o slot
        selecionarSlot(slotEncontrado.horaInicio, slotEncontrado.horaFim);
    } else {
        // Verificar se está dentro do horário de funcionamento
        const horarioMin = hora * 60 + min;
        const primeiroSlot = slotsDisponiveis.length > 0 ? slotsDisponiveis[0] : null;
        const ultimoSlot = slotsDisponiveis.length > 0 ? slotsDisponiveis[slotsDisponiveis.length - 1] : null;
        
        if (primeiroSlot && ultimoSlot) {
            const inicioMin = parseInt(primeiroSlot.horaInicio.split(':')[0]) * 60 + parseInt(primeiroSlot.horaInicio.split(':')[1]);
            const fimMin = parseInt(ultimoSlot.horaInicio.split(':')[0]) * 60 + parseInt(ultimoSlot.horaInicio.split(':')[1]);
            
            if (horarioMin < inicioMin) {
                status.textContent = `❌ Antes do horário de funcionamento (após ${primeiroSlot.horaInicio})`;
            } else if (horarioMin > fimMin) {
                status.textContent = `❌ Após o horário de funcionamento (até ${ultimoSlot.horaInicio})`;
            } else {
                status.textContent = '❌ Horário indisponível (já agendado ou conflitante)';
            }
        } else {
            status.textContent = '❌ Horário indisponível';
        }
        status.className = 'form-hint text-danger';
        input.classList.add('error');
        input.classList.remove('success');
    }
}

function selecionarSlot(horaInicio, horaFim) {
    slotSelecionado = { horaInicio, horaFim };
    document.querySelectorAll('.slot-btn').forEach(b => {
        b.classList.remove('selected');
        if (b.textContent.trim() === horaInicio) b.classList.add('selected');
    });

    // Limpar input personalizado se existir
    const horarioInput = document.getElementById('horario-personalizado');
    const status = document.getElementById('horario-personalizado-status');
    if (horarioInput) {
        horarioInput.value = horaInicio;
        horarioInput.classList.add('success');
        horarioInput.classList.remove('error');
    }
    if (status) {
        status.textContent = '✅ Horário selecionado!';
        status.className = 'form-hint text-success';
    }

    irParaStep(3);
    preencherResumo();
}

// ===================== STEP 3: FORMULÁRIO =====================

function preencherResumo() {
    document.getElementById('resumo-servico').textContent = servicoSelecionado.nome;
    document.getElementById('resumo-data').textContent = formatarDataBR(dataSelecionada);
    document.getElementById('resumo-horario').textContent = `${slotSelecionado.horaInicio} às ${slotSelecionado.horaFim}`;

    let valorTotal = parseFloat(servicoSelecionado.valor);
    adicionaisSelecionados.forEach(addId => {
        const addServico = servicosAdicionais.find(s => s.id === addId);
        if (addServico) valorTotal += parseFloat(addServico.valor);
    });

    document.getElementById('resumo-valor').textContent = formatarMoeda(valorTotal);

    const adicionaisResumo = document.getElementById('resumo-adicionais');
    if (adicionaisResumo) {
        if (adicionaisSelecionados.length > 0) {
            const nomes = adicionaisSelecionados.map(addId => {
                const s = servicosAdicionais.find(serv => serv.id === addId);
                return s ? s.nome : '';
            }).filter(Boolean).join(', ');
            adicionaisResumo.textContent = nomes;
            adicionaisResumo.closest('.resumo-row').classList.remove('hidden');
        } else {
            adicionaisResumo.closest('.resumo-row').classList.add('hidden');
        }
    }
}

async function confirmarAgendamento(event) {
    event.preventDefault();

    const nome = document.getElementById('clienteNome').value.trim();
    const nota = document.getElementById('notaOpcional').value.trim();
    const telefone = document.getElementById('telefoneContato').value.trim();

    if (!nome) {
        mostrarToast('Por favor, digite seu nome.', 'error');
        return;
    }

    if (!telefone) {
        mostrarToast('Por favor, digite seu número de WhatsApp.', 'error');
        document.getElementById('telefoneContato').focus();
        return;
    }

    const dataHoraInicio = `${dataSelecionada}T${slotSelecionado.horaInicio}:00`;

    const btn = document.getElementById('btn-confirmar');
    btn.disabled = true;
    btn.textContent = '⏳ Confirmando...';

    try {
        const result = await criarAgendamento({
            clienteNome: nome,
            servicoId: servicoSelecionado.id,
            dataHoraInicio: dataHoraInicio,
            notaOpcional: nota,
            telefoneContato: telefone,
            servicosAdicionais: adicionaisSelecionados.join(',')
        });

        ultimoAgendamento = result.agendamento;

        localStorage.setItem('ultimoAgendamento', JSON.stringify({
            hashId: result.agendamento.hashId,
            nome: nome,
            data: dataSelecionada
        }));

        // Mostrar tela de WhatsApp OBRIGATÓRIO
        mostrarTelaWhatsApp(result.agendamento);

    } catch (err) {
        mostrarToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = '✅ Confirmar Agendamento';
    }
}

// ===================== TELA DE WHATSAPP OBRIGATÓRIO =====================

function mostrarTelaWhatsApp(agendamento) {
    aguardandoWhatsApp = true;
    
    // Esconder steps 1-3
    document.getElementById('step-1-content').classList.add('hidden');
    document.getElementById('step-2-content').classList.add('hidden');
    document.getElementById('step-3-content').classList.add('hidden');
    document.getElementById('step-4-content').classList.add('hidden');

    // Mostrar tela intermediária do WhatsApp
    const whatsappScreen = document.getElementById('whatsapp-screen');
    if (whatsappScreen) {
        whatsappScreen.classList.remove('hidden');
    }

    // Preencher dados
    document.getElementById('whatsapp-cliente').textContent = agendamento.clienteNome;
    document.getElementById('whatsapp-data').textContent = formatarDataBR(dataSelecionada);
    document.getElementById('whatsapp-horario').textContent = `${slotSelecionado.horaInicio} às ${slotSelecionado.horaFim}`;
    document.getElementById('whatsapp-servico').textContent = agendamento.servico;
    document.getElementById('whatsapp-valor').textContent = formatarMoeda(agendamento.valor);

    const whatsappBtn = document.getElementById('btn-enviar-whatsapp');
    whatsappBtn.href = agendamento.whatsappUrl;
    whatsappBtn.target = '_blank';
    whatsappBtn.onclick = function(e) {
        // Marcar que o WhatsApp foi enviado
        aguardandoWhatsApp = false;
        mostrarSucesso(agendamento);
        mostrarToast('✅ Comprovante enviado! Agendamento confirmado.', 'success');
    };
}

// ===================== STEP 4: SUCESSO / TICKET =====================

function mostrarSucesso(agendamento) {
    // Esconder tela do WhatsApp
    const whatsappScreen = document.getElementById('whatsapp-screen');
    if (whatsappScreen) whatsappScreen.classList.add('hidden');

    // Mostrar step 4
    document.getElementById('step-4-content').classList.remove('hidden');
    document.querySelectorAll('.step').forEach(s => s.classList.add('completed'));

    // Preencher ticket
    document.getElementById('ticket-cliente').textContent = agendamento.clienteNome;
    document.getElementById('ticket-data').textContent = formatarDataBR(dataSelecionada);
    document.getElementById('ticket-horario').textContent = `${slotSelecionado.horaInicio} às ${slotSelecionado.horaFim}`;
    document.getElementById('ticket-servico').textContent = agendamento.servico;
    document.getElementById('ticket-valor').textContent = formatarMoeda(agendamento.valor);
    document.getElementById('ticket-codigo').textContent = agendamento.hashId;

    // Link WhatsApp no ticket
    document.getElementById('whatsapp-link').href = agendamento.whatsappUrl;
}

function baixarTicket() {
    const ticket = document.getElementById('ticket');
    if (!ticket) return;

    const logoImg = ticket.querySelector('.ticket-logo');
    const logoOriginalSrc = logoImg ? logoImg.src : null;

    function preloadLogo(callback) {
        if (!logoImg || !logoOriginalSrc) { callback(); return; }
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function() {
            const c = document.createElement('canvas');
            c.width = img.width;
            c.height = img.height;
            const ctx = c.getContext('2d');
            ctx.drawImage(img, 0, 0);
            logoImg.src = c.toDataURL('image/png');
            callback();
        };
        img.onerror = function() { callback(); };
        img.src = logoOriginalSrc;
    }

    preloadLogo(function() {
        html2canvas(ticket, {
            backgroundColor: '#161616',
            scale: 2,
            useCORS: true,
            allowTaint: true,
            logging: false
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = `comprovante-barbecity-${ultimoAgendamento?.hashId || 'ticket'}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
            mostrarToast('🖼️ Comprovante baixado!', 'success');
            if (logoImg && logoOriginalSrc) logoImg.src = logoOriginalSrc;
        }).catch(err => {
            mostrarToast('Erro ao gerar imagem. Faça um print da tela.', 'error');
            if (logoImg && logoOriginalSrc) logoImg.src = logoOriginalSrc;
        });
    });
}

// ===================== NAVEGAÇÃO ENTRE STEPS =====================

function irParaStep(step) {
    document.querySelectorAll('.step').forEach((s, i) => {
        s.classList.remove('active');
        if (i + 1 === step) s.classList.add('active');
        if (i + 1 < step) s.classList.add('completed');
    });

    document.getElementById('step-1-content').classList.toggle('hidden', step !== 1);
    document.getElementById('step-2-content').classList.toggle('hidden', step !== 2);
    document.getElementById('step-3-content').classList.toggle('hidden', step !== 3);
    document.getElementById('step-4-content').classList.add('hidden');
    
    const whatsappScreen = document.getElementById('whatsapp-screen');
    if (whatsappScreen) whatsappScreen.classList.add('hidden');
}

function voltarStep1() { irParaStep(1); }
function voltarStep2() { irParaStep(2); }
