<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meu Agendamento — BarbeCuts Jaraguá</title>
    <meta name="description" content="Consulte ou cancele seu agendamento na BarbeCuts Jaraguá pelo código ou telefone.">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="icon" href="/img/logo.jpeg" type="image/jpeg">
</head>
<body>
    <nav class="navbar" id="navbar">
        <div class="container">
            <a href="/" class="navbar-brand">
                <img src="/img/logo.jpeg" alt="BarbeCuts" class="navbar-logo">
                <div class="navbar-brand-text">BarbeCuts<span>Jaraguá</span></div>
            </a>
            <div class="navbar-links">
                <a href="/">Início</a>
                <a href="/agendamento">Agendar</a>
                <a href="/meu-agendamento" class="active">Meu Agendamento</a>
                <a href="/agendamento" class="navbar-cta">✂️ Agendar Horário</a>
            </div>
            <button class="hamburger" id="hamburger" aria-label="Menu"><span></span><span></span><span></span></button>
        </div>
    </nav>
    <div class="mobile-overlay" id="mobile-overlay"></div>
    <div class="mobile-menu" id="mobile-menu">
        <a href="/">🏠 Início</a>
        <a href="/agendamento">✂️ Agendar</a>
        <a href="/meu-agendamento" class="active">🔍 Meu Agendamento</a>
        <a href="/agendamento" class="navbar-cta" style="margin-top:1rem;justify-content:center;">✂️ Agendar Horário</a>
    </div>

    <section class="page-section" style="padding-top:7rem;">
        <div class="container">
            <div class="section-title reveal">
                <span class="section-subtitle">Consulta</span>
                <h2>🔍 Meu <span class="highlight">Agendamento</span></h2>
                <div class="gold-divider"></div>
                <p>Consulte ou cancele seu agendamento.</p>
            </div>

            <!-- Tabs -->
            <div style="display:flex;gap:0.5rem;justify-content:center;margin-bottom:1.5rem;">
                <button class="tab-btn active" id="tab-codigo-btn" onclick="mostrarAba('codigo')">🔑 Por Código</button>
                <button class="tab-btn" id="tab-telefone-btn" onclick="mostrarAba('telefone')">📱 Por Telefone</button>
            </div>

            <!-- CÓDIGO -->
            <div id="aba-codigo">
                <div class="card" style="max-width:500px;margin:0 auto;">
                    <div class="card-header"><span class="card-title">🔑 Consultar por Código</span></div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label" for="hash-input">Código do Agendamento</label>
                            <input type="text" id="hash-input" class="form-input" placeholder="Ex: a1b2c3d4e5" maxlength="20" style="font-family:var(--font-mono);letter-spacing:2px;text-align:center;">
                            <p class="form-hint">Informe o código recebido na confirmação.</p>
                        </div>
                        <button class="btn btn-primary btn-block" onclick="buscarPorCodigo()">🔍 Consultar</button>
                    </div>
                </div>
            </div>

            <!-- TELEFONE -->
            <div id="aba-telefone" class="hidden">
                <div class="card" style="max-width:500px;margin:0 auto;">
                    <div class="card-header"><span class="card-title">📱 Consultar por Telefone</span></div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label" for="tel-input">Seu WhatsApp / Telefone</label>
                            <input type="text" id="tel-input" class="form-input" placeholder="(11) 91504-0871" maxlength="20">
                            <p class="form-hint">Informe o telefone usado no agendamento.</p>
                        </div>
                        <button class="btn btn-primary btn-block" onclick="buscarPorTelefone()">🔍 Consultar</button>
                    </div>
                </div>
            </div>

            <!-- Loading -->
            <div id="loading-consulta" class="loading hidden" style="margin-top:1rem;"><div class="spinner"></div><p style="margin-left:0.75rem;">Consultando...</p></div>

            <!-- Error -->
            <div id="error-consulta" class="card hidden" style="max-width:500px;margin:1rem auto 0;border-color:var(--danger);">
                <div class="card-body" style="text-align:center;">
                    <div style="font-size:3rem;margin-bottom:0.5rem;">❌</div>
                    <p id="error-message" class="text-danger">Nenhum agendamento encontrado.</p>
                </div>
            </div>

            <!-- Result -->
            <div id="result-consulta" class="hidden" style="max-width:500px;margin:1.5rem auto 0;"></div>
            <div id="result-multi" class="hidden" style="max-width:500px;margin:1.5rem auto 0;"></div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-brand-section">
                    <div class="footer-brand-title">✂️ BarbeCuts Jaraguá</div>
                    <p class="footer-brand-desc">Tradição e estilo em cada corte.</p>
                    <div class="footer-social">
                        <a href="https://wa.me/5511972244484" target="_blank">📱</a>
                        <a href="https://www.instagram.com" target="_blank">📷</a>
                    </div>
                </div>
                <div>
                    <h4>Links</h4>
                    <ul class="footer-links">
                        <li><a href="/">Início</a></li>
                        <li><a href="/agendamento">Agendar Horário</a></li>
                        <li><a href="/meu-agendamento">Meu Agendamento</a></li>
                    </ul>
                </div>
                <div>
                    <h4>Contato</h4>
                    <div class="footer-contact">
                        <p>📱 <a href="https://wa.me/5511915040871" target="_blank">(11) 91504-0871</a></p>
                        <p>📍 Jaraguá, São Paulo</p>
                        <p>🕐 Ter-Dom: 09h às 20h</p>
                    </div>
                </div>
            </div>
            <div class="footer-bottom"><p>© 2026 BarbeCuts Jaraguá.</p><div class="footer-faith">"Deus é Fiel" ✝️</div></div>
        </div>
    </footer>

    <a href="https://wa.me/5511972244484" target="_blank" class="float-whatsapp">📱</a>

    <script src="/js/api.js"></script>
    <script>
        var currentHash = '';

        document.addEventListener('DOMContentLoaded', function() {
            var navbar = document.getElementById('navbar');
            window.addEventListener('scroll', function() { navbar.classList.toggle('scrolled', window.scrollY > 50); });
            var hamburger = document.getElementById('hamburger');
            var mobileMenu = document.getElementById('mobile-menu');
            var overlay = document.getElementById('mobile-overlay');
            function toggleMenu() {
                hamburger.classList.toggle('active');
                mobileMenu.classList.toggle('open');
                overlay.classList.toggle('open');
                document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
            }
            hamburger.addEventListener('click', toggleMenu);
            overlay.addEventListener('click', toggleMenu);
            mobileMenu.querySelectorAll('a').forEach(function(l) { l.addEventListener('click', toggleMenu); });

            var params = new URLSearchParams(window.location.search);
            var hashParam = params.get('hash');
            if (hashParam) {
                document.getElementById('hash-input').value = hashParam;
                buscarPorCodigo();
            }
            document.getElementById('hash-input').addEventListener('keypress', function(e) { if (e.key === 'Enter') buscarPorCodigo(); });
            document.getElementById('tel-input').addEventListener('keypress', function(e) { if (e.key === 'Enter') buscarPorTelefone(); });
        });

        function mostrarToast(msg, tipo) {
            var existing = document.querySelector('.toast');
            if (existing) existing.remove();
            var toast = document.createElement('div');
            toast.className = 'toast toast-' + (tipo || 'info');
            toast.textContent = msg;
            document.body.appendChild(toast);
            setTimeout(function() { toast.remove(); }, 4500);
        }

        function mostrarAba(aba) {
            document.getElementById('aba-codigo').classList.toggle('hidden', aba !== 'codigo');
            document.getElementById('aba-telefone').classList.toggle('hidden', aba !== 'telefone');
            document.getElementById('tab-codigo-btn').classList.toggle('active', aba === 'codigo');
            document.getElementById('tab-telefone-btn').classList.toggle('active', aba === 'telefone');
            document.getElementById('result-consulta').classList.add('hidden');
            document.getElementById('result-multi').classList.add('hidden');
            document.getElementById('error-consulta').classList.add('hidden');
        }

        function criarCardAgendamento(ag, podeCancelar) {
            var dateStr = ag.dataHoraInicio || '';
            var dataFormatada = '—', horaFormatada = '—';
            if (dateStr) {
                var dateObj = new Date(dateStr);
                dataFormatada = dateObj.toLocaleDateString('pt-BR');
                horaFormatada = dateObj.toLocaleTimeString('pt-BR', { hour:'2-digit', minute:'2-digit' });
            }
            var status = ag.status || 'agendado';
            var statusLabels = { 'agendado':'🟡 Agendado', 'concluido':'✅ Concluído', 'cancelado':'❌ Cancelado', 'ausente':'⚪ Ausente' };
            var telefone = ag.telefoneContato || '—';
            var cancelBtn = '';
            if (podeCancelar && status === 'agendado') {
                cancelBtn = '<button class="btn btn-danger btn-block" style="margin-top:1rem;" onclick="cancelarAgendamento(\'' + (ag.hashId || '') + '\')">🗑️ Cancelar Agendamento</button>';
            }
            return '<div class="resumo-card" style="margin-bottom:1rem;">' +
                '<div class="resumo-row"><span class="resumo-label">Cliente</span><span class="resumo-value">' + (ag.clienteNome || '—') + '</span></div>' +
                '<div class="resumo-row"><span class="resumo-label">Serviço</span><span class="resumo-value">' + (ag.servico || '—') + '</span></div>' +
                '<div class="resumo-row"><span class="resumo-label">Data</span><span class="resumo-value">' + dataFormatada + '</span></div>' +
                '<div class="resumo-row"><span class="resumo-label">Horário</span><span class="resumo-value">' + horaFormatada + '</span></div>' +
                '<div class="resumo-row"><span class="resumo-label">Valor</span><span class="resumo-value resumo-total">R$ ' + parseFloat(ag.valor || 0).toFixed(2) + '</span></div>' +
                '<div class="resumo-row"><span class="resumo-label">Status</span><span class="resumo-value">' + (statusLabels[status] || status) + '</span></div>' +
                (telefone !== '—' ? '<div class="resumo-row"><span class="resumo-label">Telefone</span><span class="resumo-value">📱 ' + telefone + '</span></div>' : '') +
                '</div>' + cancelBtn;
        }

        async function buscarPorCodigo() {
            var hash = document.getElementById('hash-input').value.trim();
            if (!hash || hash.length < 3) {
                mostrarToast('Informe o código do agendamento.', 'error');
                return;
            }
            currentHash = hash;
            var loading = document.getElementById('loading-consulta');
            var result = document.getElementById('result-consulta');
            var multi = document.getElementById('result-multi');
            var error = document.getElementById('error-consulta');
            loading.classList.remove('hidden');
            result.classList.add('hidden');
            multi.classList.add('hidden');
            error.classList.add('hidden');
            try {
                var data = await consultarAgendamento(hash);
                var ag = data.agendamento;
                result.innerHTML = criarCardAgendamento(ag, true);
                result.classList.remove('hidden');
            } catch (err) {
                document.getElementById('error-message').textContent = err.message || 'Agendamento não encontrado. Verifique o código.';
                error.classList.remove('hidden');
            } finally {
                loading.classList.add('hidden');
            }
        }

        async function buscarPorTelefone() {
            var tel = document.getElementById('tel-input').value.trim();
            if (!tel) {
                mostrarToast('Informe seu telefone.', 'error');
                return;
            }
            var loading = document.getElementById('loading-consulta');
            var result = document.getElementById('result-consulta');
            var multi = document.getElementById('result-multi');
            var error = document.getElementById('error-consulta');
            loading.classList.remove('hidden');
            result.classList.add('hidden');
            multi.classList.add('hidden');
            error.classList.add('hidden');
            try {
                var data = await buscarAgendamentosPorTelefone(tel);
                var ags = data.agendamentos || [];
                if (ags.length === 0) {
                    document.getElementById('error-message').textContent = 'Nenhum agendamento encontrado para este telefone.';
                    error.classList.remove('hidden');
                    loading.classList.add('hidden');
                    return;
                }
                if (ags.length === 1) {
                    result.innerHTML = criarCardAgendamento(ags[0], true);
                    result.classList.remove('hidden');
                } else {
                    var html = '<h3 style="font-family:var(--font-display);color:var(--brand-primary);margin-bottom:1rem;">📋 ' + ags.length + ' agendamentos encontrados</h3>';
                    ags.forEach(function(ag) { html += criarCardAgendamento(ag, true); });
                    multi.innerHTML = html;
                    multi.classList.remove('hidden');
                }
            } catch (err) {
                document.getElementById('error-message').textContent = err.message || 'Erro ao buscar.';
                error.classList.remove('hidden');
            } finally {
                loading.classList.add('hidden');
            }
        }

        async function cancelarAgendamento(hashId) {
            if (!hashId) return;
            if (!confirm('Tem certeza que deseja cancelar este agendamento?')) return;
            try {
                var result = await cancelarAgendamentoCliente(hashId);
                mostrarToast('✅ Agendamento cancelado com sucesso!', 'success');
                if (!document.getElementById('aba-codigo').classList.contains('hidden')) {
                    buscarPorCodigo();
                } else {
                    buscarPorTelefone();
                }
            } catch (err) {
                mostrarToast(err.message || 'Erro ao cancelar.', 'error');
            }
        }
    </script>
</body>
</html>
