/**
 * agendamento.js — Lógica completa da página de agendamento
 * ==========================================================
 * Gerencia as 4 etapas: Serviço → Data/Horário → Dados → Ticket
 * Tema: BarbeCity Jaraguá
 */

let servicos = [];
let servicosAdicionais = [];
let servicoSelecionado = null;
let adicionaisSelecionados = [];
let dataSelecionada = null;
let slotSelecionado = null;
let ultimoAgendamento = null;

document.addEventListener('DOMContentLoaded', async () => {
    await carregarServicos();
    gerarDiasDisponiveis();
    setupHamburger();

    // Adicionar event listener ao formulário (em vez de onsubmit)
    const form = document.getElementById('agendamento-form');
    if (form) {
        form.addEventListener('submit', confirmarAgendamento);
    }

    // Formatação automática do telefone
    const telefoneInput = document.getElementById('telefoneContato');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', formatarTelefone);
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
    
    if (valor.length > 11) {
        valor = valor.slice(0, 11);
    }
    
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
        // Serviços principais (cortes individuais)
        const cortes = data.servicos.filter(s => s.tipo === 'principal');
        // Serviços adicionais (Botox, Luzes)
        servicosAdicionais = data.servicos.filter(s => s.tipo === 'adicional');
        // Combos
        const combos = data.servicos.filter(s => s.tipo === 'combo');
        
        // Todos os serviços selecionáveis (cortes + combos)
        servicos = [...cortes, ...combos];
        
        const container = document.getElementById('servicos-selecao');
        container.innerHTML = '';

        if (servicos.length === 0) {
            container.innerHTML = '<p class="text-secondary" style="text-align: center;">Nenhum serviço disponível.</p>';
            return;
        }

        // Seção de Cortes
        if (cortes.length > 0) {
            const secaoCortes = document.createElement('div');
            secaoCortes.className = 'secao-servicos';
            secaoCortes.innerHTML = '<h3 class="secao-titulo">✂️ Cortes</h3><div class="grid grid-2 grid-servicos"></div>';
            const gridCortes = secaoCortes.querySelector('.grid-servicos');
            
            cortes.forEach(s => {
                gridCortes.appendChild(criarCardServico(s));
            });
            
            container.appendChild(secaoCortes);
        }

        // Seção de Adicionais (selecionáveis sozinhos)
        if (servicosAdicionais.length > 0) {
            const secaoAdicionais = document.createElement('div');
            secaoAdicionais.className = 'secao-servicos';
            secaoAdicionais.innerHTML = '<h3 class="secao-titulo">✨ Adicionais</h3><div class="grid grid-2 grid-servicos"></div>';
            const gridAdicionais = secaoAdicionais.querySelector('.grid-servicos');
            
            servicosAdicionais.forEach(s => {
                gridAdicionais.appendChild(criarCardServico(s));
            });
            
            container.appendChild(secaoAdicionais);
        }

        // Seção de Combos
        if (combos.length > 0) {
            const secaoCombos = document.createElement('div');
            secaoCombos.className = 'secao-servicos';
            secaoCombos.innerHTML = '<h3 class="secao-titulo">🔥 Combos</h3><div class="grid grid-2 grid-servicos"></div>';
            const gridCombos = secaoCombos.querySelector('.grid-servicos');
            
            combos.forEach(s => {
                gridCombos.appendChild(criarCardServico(s));
            });
            
            container.appendChild(secaoCombos);
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
    
    // Escolher ícone baseado no nome/tipo do serviço
    let icone = getIconeServico(s);
    
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
    const tipo = s.tipo;
    
    if (tipo === 'combo') return '🔥';
    if (tipo === 'adicional') {
        if (nomeLower.includes('botox')) return '💉';
        if (nomeLower.includes('luzes')) return '💡';
        return '✨';
    }
    
    // Cortes principais
    if (nomeLower.includes('corte') && nomeLower.includes('barba')) return '✂️';
    if (nomeLower.includes('corte')) return '✂️';
    if (nomeLower.includes('barba')) return '🪒';
    if (nomeLower.includes('sobrancelha')) return '✨';
    
    return '✂️';
}

function selecionarServico(id) {
    // Verificar se é um serviço adicional selecionado como principal
    const servicoAdd = servicosAdicionais.find(s => s.id === id);
    if (servicoAdd) {
        servicoSelecionado = servicoAdd;
    } else {
        servicoSelecionado = servicos.find(s => s.id === id);
    }
    
    if (!servicoSelecionado) return;

    // Destacar selecionado
    document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
    document.querySelector(`.service-card[data-id="${id}"]`).classList.add('selected');

    // Avançar para step 2
    irParaStep(2);
    carregarSlots();
    renderizarAdicionais();
}

function renderizarAdicionais() {
    const container = document.getElementById('adicionais-container');
    if (!container) return;
    
    container.innerHTML = '';

    // Se o serviço selecionado já é um adicional (Botox ou Luzes),
    // remover ele da lista de adicionais disponíveis
    let adicionaisDisponiveis = [...servicosAdicionais];
    
    if (servicoSelecionado && servicoSelecionado.tipo === 'adicional') {
        adicionaisDisponiveis = adicionaisDisponiveis.filter(s => s.id !== servicoSelecionado.id);
    }

    if (adicionaisDisponiveis.length === 0) {
        container.innerHTML = '<p class="text-secondary" style="font-size: 0.9rem;">Nenhum adicional disponível para este serviço.</p>';
        return;
    }

    adicionaisDisponiveis.forEach(s => {
        const card = document.createElement('div');
        card.className = 'service-card service-card-sm';
        card.dataset.id = s.id;
        
        const isSelected = adicionaisSelecionados.includes(s.id);
        if (isSelected) {
            card.classList.add('selected');
        }
        
        card.onclick = () => toggleAdicional(s.id);
        
        let icone = '✨';
        const nomeLower = s.nome.toLowerCase();
        if (nomeLower.includes('botox')) icone = '💉';
        if (nomeLower.includes('luzes')) icone = '💡';
        
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
    if (index === -1) {
        adicionaisSelecionados.push(id);
    } else {
        adicionaisSelecionados.splice(index, 1);
    }
    
    // Atualizar visual
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

    // Mostrar 14 dias à frente
    for (let i = 0; i < 14; i++) {
        const data = new Date(hoje);
        data.setDate(hoje.getDate() + i);

        // Formatar data localmente para evitar problemas de fuso horário (UTC)
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
        btn.innerHTML = `
            <span class="date-day">${diasSemana[diaSemana]}</span>
            <span class="date-num">${diaMes}/${mes}</span>
        `;
        btn.onclick = () => selecionarData(dataStr);

        container.appendChild(btn);
    }
}

function selecionarData(dataStr) {
    dataSelecionada = dataStr;

    // Destacar botão selecionado
    document.querySelectorAll('.date-btn').forEach(b => {
        b.classList.remove('selected');
        if (b.dataset.data === dataStr) {
            b.classList.add('selected');
        }
    });

    carregarSlots();
}

async function carregarSlots() {
    if (!servicoSelecionado || !dataSelecionada) return;

    const container = document.getElementById('slots-container');
    mostrarLoading(container);

    try {
        const data = await buscarHorarios(dataSelecionada, servicoSelecionado.id);
        const slots = data.slotsDisponiveis || [];

        if (slots.length === 0) {
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
        html += '<div class="slots-grid">';

        slots.forEach(s => {
            html += `<button class="slot-btn" onclick="selecionarSlot('${s.horaInicio}', '${s.horaFim}')">
                ${s.horaInicio}
            </button>`;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch (err) {
        container.innerHTML = `<p class="text-danger">Erro ao carregar horários: ${err.message}</p>`;
    }
}

function selecionarSlot(horaInicio, horaFim) {
    slotSelecionado = { horaInicio, horaFim };

    // Destacar slot
    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.slot-btn').forEach(b => {
        if (b.textContent.trim() === horaInicio) {
            b.classList.add('selected');
        }
    });

    // Avançar para step 3
    irParaStep(3);
    preencherResumo();
}

// ===================== STEP 3: FORMULÁRIO =====================

function preencherResumo() {
    document.getElementById('resumo-servico').textContent = servicoSelecionado.nome;
    document.getElementById('resumo-data').textContent = formatarDataBR(dataSelecionada);
    document.getElementById('resumo-horario').textContent = `${slotSelecionado.horaInicio} às ${slotSelecionado.horaFim}`;
    
    // Calcular valor total com adicionais
    let valorTotal = parseFloat(servicoSelecionado.valor);
    let adicionaisTexto = '';
    
    adicionaisSelecionados.forEach(addId => {
        const addServico = servicosAdicionais.find(s => s.id === addId);
        if (addServico) {
            valorTotal += parseFloat(addServico.valor);
            adicionaisTexto += ` + ${addServico.nome}`;
        }
    });
    
    document.getElementById('resumo-valor').textContent = formatarMoeda(valorTotal);
    
    // Mostrar adicionais selecionados no resumo
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

    // Montar data/hora ISO
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

        // Salvar no localStorage
        localStorage.setItem('ultimoAgendamento', JSON.stringify({
            hashId: result.agendamento.hashId,
            nome: nome,
            data: dataSelecionada
        }));

        // Mostrar tela de sucesso
        mostrarSucesso(result.agendamento);

    } catch (err) {
        mostrarToast(err.message, 'error');
        btn.disabled = false;
        btn.textContent = '✅ Confirmar Agendamento';
    }
}

// ===================== STEP 4: SUCESSO / TICKET =====================

function mostrarSucesso(agendamento) {
    // Esconder steps 1-3
    document.getElementById('step-1-content').classList.add('hidden');
    document.getElementById('step-2-content').classList.add('hidden');
    document.getElementById('step-3-content').classList.add('hidden');
    document.getElementById('step-4-content').classList.remove('hidden');

    // Atualizar steps indicator
    document.querySelectorAll('.step').forEach(s => s.classList.add('completed'));

    // Preencher ticket
    document.getElementById('ticket-cliente').textContent = agendamento.clienteNome;
    document.getElementById('ticket-data').textContent = formatarDataBR(dataSelecionada);
    document.getElementById('ticket-horario').textContent = `${slotSelecionado.horaInicio} às ${slotSelecionado.horaFim}`;
    document.getElementById('ticket-servico').textContent = agendamento.servico;
    document.getElementById('ticket-valor').textContent = formatarMoeda(agendamento.valor);
    document.getElementById('ticket-codigo').textContent = agendamento.hashId;

    // Link WhatsApp
    document.getElementById('whatsapp-link').href = agendamento.whatsappUrl;

    mostrarToast('✅ Agendamento confirmado com sucesso!', 'success');
}

function baixarTicket() {
    const ticket = document.getElementById('ticket');
    if (!ticket) return;

    // Pré-carregar a logo como base64 para evitar problemas de CORS em mobile
    const logoImg = ticket.querySelector('.ticket-logo');
    const logoOriginalSrc = logoImg ? logoImg.src : null;

    // Criar um canvas temporário para converter a logo em base64
    function preloadLogo(callback) {
        if (!logoImg || !logoOriginalSrc) {
            callback();
            return;
        }
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
        img.onerror = function() {
            // Se falhar, mantém a original
            callback();
        };
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
            // Restaurar logo original
            if (logoImg && logoOriginalSrc) {
                logoImg.src = logoOriginalSrc;
            }
        }).catch(err => {
            mostrarToast('Erro ao gerar imagem. Faça um print da tela.', 'error');
            // Restaurar logo original
            if (logoImg && logoOriginalSrc) {
                logoImg.src = logoOriginalSrc;
            }
        });
    });
}

// ===================== NAVEGAÇÃO ENTRE STEPS =====================

function irParaStep(step) {
    // Atualizar indicador
    document.querySelectorAll('.step').forEach((s, i) => {
        s.classList.remove('active');
        if (i + 1 === step) s.classList.add('active');
        if (i + 1 < step) s.classList.add('completed');
    });

    // Mostrar/esconder conteúdos
    document.getElementById('step-1-content').classList.toggle('hidden', step !== 1);
    document.getElementById('step-2-content').classList.toggle('hidden', step !== 2);
    document.getElementById('step-3-content').classList.toggle('hidden', step !== 3);
    document.getElementById('step-4-content').classList.add('hidden');
}

function voltarStep1() {
    irParaStep(1);
}

function voltarStep2() {
    irParaStep(2);
}
