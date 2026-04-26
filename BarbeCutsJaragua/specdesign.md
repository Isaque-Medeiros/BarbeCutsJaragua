# 🎨 SPEC DESIGN — Sistema BarbeCity Jaraguá (Anderson Barbeiro)

> **Arquivo:** `specdesign.md`
> **Baseado em:** `VIsualEspecificacao.md` + Projeto atual + Logo `logo.jpeg`
> **Data:** Abril/2026

---

## 🔍 1. Análise do Logo (`logo.jpeg`)

O logotipo da **BarbeCity Jaraguá** foi analisado e apresenta os seguintes atributos visuais:

| Elemento | Característica |
|----------|----------------|
| **Nome** | "BarbeCity Jaraguá" |
| **Estilo** | Industrial / Urbano / Tradicional |
| **Cor Dominante** | Vermelho Bordô (#8B0000) |
| **Cores de Apoio** | Cinza Grafite, Branco, Dourado/Madeira |
| **Sensação** | Barberia clássica com pegada moderna urbana |
| **Público-alvo** | Homens que valorizam estilo, tradição e atendimento personalizado |

### 📐 Como o logo deve ser enquadrado no design:

1. **Navbar** — O logo deve aparecer no canto esquerdo da barra de navegação, substituindo o texto "✂️ Barbearia" atual. Tamanho sugerido: 40-48px de altura.
2. **Hero/Home** — O logo deve ser o centro visual da home, com destaque e assinatura "Anderson Barbeiro" abaixo.
3. **Ticket/Comprovante** — O logo deve aparecer no topo do ticket de confirmação de agendamento.
4. **Admin** — Versão simplificada (apenas ícone ou marca d'água) no canto superior.
5. **Favicon** — Extrair um ícone do logo para substituir o emoji atual.

---

## 🎯 2. Identidade Visual (Refinada)

### 2.1 Paleta de Cores — Tema "BarbeCity Dark"

```css
/* Paleta Principal */
--primary: #8B0000;        /* Vermelho Bordô → Cor do logo */
--primary-dark: #5C0000;   /* Bordô escuro para hover */
--primary-light: #B22222;  /* Bordô mais claro para detalhes */

/* Fundo (Dark Mode Profundo) */
--bg-deep: #0A0A0A;        /* Fundo mais escuro que o atual (#0D0D0D) */
--bg-surface: #161616;     /* Cards e superfícies (#1A1A1A atualmente) */
--bg-elevated: #222222;    /* Elementos elevados (#2A2A2A atualmente) */

/* Texto */
--text-primary: #F0F0F0;   /* Quase branco */
--text-secondary: #909090; /* Cinza médio para legendas */
--text-muted: #606060;     /* Placeholder */

/* Destaque */
--gold: #D4AF37;           /* Dourado metálico → botões CTA, bordas de cards */
--gold-hover: #C49B2C;     /* Dourado escuro hover */
--gold-soft: rgba(212, 175, 55, 0.15); /* Dourado translúcido para backgrounds */

/* Bordas */
--border: #2C2C2C;         /* Borda sutil */
--border-gold: rgba(212, 175, 55, 0.3); /* Borda dourada para cards especiais */

/* Semântica */
--success: #2ECC71;
--warning: #F1C40F;
--danger: #E74C3C;
--info: #3498DB;
```

### 2.2 Tipografia

```css
/* Títulos & Display — Serifada Robusta / Industrial */
--font-display: 'Playfair Display', 'Georgia', serif;
/* Uso: Logo, títulos de seção, nome da barbearia */

/* Corpo — Limpa e legível */
--font-body: 'Inter', 'Segoe UI', system-ui, sans-serif;
/* Uso: Textos corridos, formulários, tabelas */

/* Mono — Para códigos e hash */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
/* Uso: Código do agendamento no ticket */
```

### 2.3 Iconografia

Substituir emojis por ícones SVG consistentes:

| Contexto Atual (emoji) | Substituir por |
|------------------------|----------------|
| ✂️ Navbar | Logo da barbearia |
| 💇‍♂️ Serviços | Ícone de tesoura/pente |
| 📅 Data | Ícone de calendário |
| ⏰ Horário | Ícone de relógio |
| 📝 Observações | Ícone de lápis |
| 📱 QR Code | Ícone de QR |
| ✅ Confirmação | Ícone de check circular |
| 📲 WhatsApp | Ícone do WhatsApp |
| 🖼️ Download | Ícone de download |
| 🔍 Consulta | Ícone de lupa |

> **Fonte dos ícones:** Lucide React ou Phosphor Icons (SVG inline ou sprite).

---

## 📐 3. Estrutura de Layout (Wireframe Detalhado)

### 3.1 Página Inicial (Home)

```
┌─────────────────────────────────────────────┐
│  NAVBAR                                      │
│  [LOGO]  Início | Agendar | Meu Agendamento  │
├─────────────────────────────────────────────┤
│                                              │
│   ┌── HERO SECTION ──────────────────────┐  │
│   │                                       │  │
│   │        [LOGO GRANDE]                  │  │
│   │                                       │  │
│   │   Anderson Barbeiro                   │  │
│   │   "Tradição e estilo em cada corte"    │  │
│   │                                       │  │
│   │   ┌─────────────────────────────┐     │  │
│   │   │  ✂️ AGENDAR HORÁRIO         │     │  │
│   │   └─────────────────────────────┘     │  │
│   │                                       │  │
│   └───────────────────────────────────────┘  │
│                                              │
│   ┌── SERVIÇOS ──────────────────────────┐  │
│   │                                       │  │
│   │  ┌─────────┐  ┌─────────┐            │  │
│   │  │ Corte   │  │ Barba   │            │  │
│   │  │ R$ 35   │  │ R$ 25   │            │  │
│   │  │ 30 min  │  │ 20 min  │            │  │
│   │  └─────────┘  └─────────┘            │  │
│   │                                       │  │
│   └───────────────────────────────────────┘  │
│                                              │
│   ┌── QR CODE ───────────────────────────┐  │
│   │   [QR CODE]                           │  │
│   │   Escaneie para agendar               │  │
│   └───────────────────────────────────────┘  │
│                                              │
├─────────────────────────────────────────────┤
│  FOOTER                                      │
│  ✂️ BarbeCity Jaraguá — "Deus é Fiel"        │
│  📱 WhatsApp: (11) 97224-4484                │
└─────────────────────────────────────────────┘
```

### 3.2 Página de Agendamento (3 Etapas + Ticket)

```
┌─────────────────────────────────────────────┐
│  NAVBAR                                      │
├─────────────────────────────────────────────┤
│                                              │
│  ┌── STEP INDICATOR ──────────────────────┐  │
│  │  ●━━━━━━○━━━━━━○━━━━━━○                │  │
│  │  1         2      3      ✔️              │  │
│  │  Serviço  Data   Dados  Ticket          │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌── (STEP 1) SELEÇÃO DE SERVIÇO ────────┐  │
│  │                                         │  │
│  │  ┌──────────────────┐  ┌──────────────┐│  │
│  │  │ 🟢 Corte Social  │  │ Corte Degradê││  │
│  │  │ R$ 35 · 30 min   │  │ R$ 45 · 45min││  │
│  │  └──────────────────┘  └──────────────┘│  │
│  │                                         │  │
│  └─────────────────────────────────────────┘  │
│                                              │
│  ┌── (STEP 2) DATA E HORÁRIO ────────────┐  │
│  │                                         │  │
│  │  [Seg 12] [Ter 13] [Qua 14] ...        │  │
│  │                                         │  │
│  │  ┌── HORÁRIOS DISPONÍVEIS ──────────┐  │  │
│  │  │  09:00 │ 09:40 │ 10:20 │ 11:00   │  │  │
│  │  │  13:00 │ 13:40 │ 14:20 │ 15:00   │  │  │
│  │  └───────────────────────────────────┘  │  │
│  │                                         │  │
│  └─────────────────────────────────────────┘  │
│                                              │
│  ┌── (STEP 3) DADOS DO CLIENTE ──────────┐  │
│  │                                         │  │
│  │  👤 Seu Nome: [___________]            │  │
│  │  📝 Observações: [___________]         │  │
│  │  📱 WhatsApp: [___________]            │  │
│  │                                         │  │
│  │  ┌── RESUMO ──────────────────────┐    │  │
│  │  │ Corte Social · 12/05 · 14:00   │    │  │
│  │  │            ──────────────       │    │  │
│  │  │            R$ 35,00             │    │  │
│  │  └────────────────────────────────┘    │  │
│  │                                         │  │
│  │  ┌─────────────────────────────┐       │  │
│  │  │  ✅ CONFIRMAR AGENDAMENTO   │       │  │
│  │  └─────────────────────────────┘       │  │
│  │                                         │  │
│  └─────────────────────────────────────────┘  │
│                                              │
│  ┌── (STEP 4) TICKET DE CONFIRMAÇÃO ──────┐  │
│  │                                         │  │
│  │    ┌──────────────────────────────┐     │  │
│  │    │   🟥 BARCECITY JARAGUÁ 🟥   │     │  │
│  │    │                              │     │  │
│  │    │   ─── ─── ─── ─── ─── ───    │     │  │
│  │    │                              │     │  │
│  │    │   👤 Cliente: João           │     │  │
│  │    │   📅 Data: 12/05/2026       │     │  │
│  │    │   ⏰ Horário: 14:00 às 14:30│     │  │
│  │    │   💇 Serviço: Corte Social  │     │  │
│  │    │   💰 Valor: R$ 35,00        │     │  │
│  │    │   🔑 Cód: a1b2c3d4e5       │     │  │
│  │    │                              │     │  │
│  │    │   ─── ─── ─── ─── ─── ───    │     │  │
│  │    │                              │     │  │
│  │    │   "Deus é Fiel" ✝️           │     │  │
│  │    └──────────────────────────────┘     │  │
│  │                                         │  │
│  │  [📲 WhatsApp]  [🖼️ Baixar Imagem]     │  │
│  │                                         │  │
│  └─────────────────────────────────────────┘  │
│                                              │
├─────────────────────────────────────────────┤
│  FOOTER                                      │
└─────────────────────────────────────────────┘
```

### 3.3 Painel Admin

```
┌─────────────────────────────────────────────┐
│  NAVBAR | ⚙️ Admin BarbeCity                │
│  ← Site | Painel                            │
├─────────────────────────────────────────────┤
│                                              │
│  ┌── FILTROS ────────────────────────────┐  │
│  │  [● Hoje] [○ Semana] [○ Mês]          │  │
│  │                       [+] Novo Serviço │  │
│  │                       [🔒 Bloquear]    │  │
│  │                       [🚪 Sair]        │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌── STATS ──────────────────────────────┐  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │  │
│  │  │R$ 350│ │R$ 400│ │  5   │ │  8   │ │  │
│  │  │ Liq. │ │ Bruto│ │Conc. │ │Agend.│ │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌── TABELA AGENDAMENTOS ────────────────┐  │
│  │  Horário │ Cliente │ Serviço │ Status  │  │
│  │  ────────┼─────────┼─────────┼──────── │  │
│  │  14:00   │ João    │ Corte   │ 🟡      │  │
│  │  15:00   │ Maria   │ Barba   │ 🟢      │  │
│  │  16:00   │ José    │ Degradê │ 🔴      │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌── SERVIÇOS ───────────────────────────┐  │
│  │  Nome │ Duração │ Valor │ Ativo │ ✏️  │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌── BLOQUEIOS ──────────────────────────┐  │
│  │  15/05 - Dia inteiro - Feriado    [✕] │  │
│  │  20/05 - 12:00 às 13:00 - Almoço [✕] │  │
│  └───────────────────────────────────────┘  │
│                                              │
├─────────────────────────────────────────────┤
│  FOOTER                                      │
└─────────────────────────────────────────────┘
```

---

## 📱 4. Design Responsivo (Mobile-First)

### 4.1 Breakpoints

```css
/* Mobile pequeno */  @media (max-width: 480px)
/* Mobile grande */   @media (min-width: 481px) and (max-width: 768px)
/* Tablet */          @media (min-width: 769px) and (max-width: 1024px)
/* Desktop */         @media (min-width: 1025px)
```

### 4.2 Comportamento Mobile

- **Navbar:** Transformar em hamburger menu com drawer lateral
- **Grid de serviços:** 1 coluna no mobile, 2 no tablet, 3+ no desktop
- **Slots de horário:** 2 colunas no mobile, 3 no tablet, auto-fill no desktop
- **Stats (admin):** 2 colunas no mobile, 3 no tablet, 6 no desktop
- **Botões:** Mínimo 48px de altura para tap targets
- **Ticket:** Largura total com padding reduzido
- **Modal:** Tela cheia no mobile

### 4.3 Touch Targets (para o Anderson usar no celular)

> Requisito especial: **Tap Targets grandes** — botões com no mínimo 48x48px, espaçamento de 8px entre elementos clicáveis.

---

## 🧩 5. Componentes de UI (Especificações)

### 5.1 Navbar
- **Background:** `--bg-surface` com `backdrop-filter: blur(12px)`
- **Altura:** 64px (mobile: 56px)
- **Logo:** Imagem real do logo, 40x40px, com nome ao lado
- **Links:** Hover com underline gradiente bordô
- **Ativo:** Borda inferior dourada (`--gold`)

### 5.2 Hero Section
- Background com gradiente sutil: `linear-gradient(180deg, #0A0A0A 0%, #161616 100%)`
- Logo grande centralizado (200x200px max)
- Nome do barbeiro com fonte display
- Botão CTA com efeito de brilho dourado

### 5.3 Service Card
- Background: `--bg-elevated`
- Borda: `1px solid var(--border)`
- Selecionado: Borda dourada `2px solid var(--gold)`, fundo `--gold-soft`
- Preço em destaque com cor dourada
- Ícone consistente (SVG) ao lado do nome

### 5.4 Step Indicator
- Bolinhas numeradas com linha conectando
- Completed: Fundo dourado com check
- Active: Borda dourada
- Inactive: Fundo escuro

### 5.5 Ticket de Confirmação
- Background: `--bg-surface`
- Borda: `2px dashed var(--gold)`
- Header com logo e nome da barbearia
- Informações em layout limpo com labels em secondary
- Código em destaque com `--font-mono`
- Assinatura "Deus é Fiel" no final
- Sombra suave para efeito de papel

### 5.6 Botão WhatsApp
- Background: `#25D366`
- Ícone SVG do WhatsApp antes do texto
- Hover: `#1DA851`

### 5.7 Modal
- Overlay com `backdrop-filter: blur(4px)`
- Card central com borda sutil
- Fechar com "X" no canto superior direito
- Animação de fade in

### 5.8 Toast Notifications
- Posição: Topo direito (mobile: topo centralizado)
- Cores por tipo: verde (success), vermelho (error), dourado (info)
- Animação slide-in da direita

### 5.9 Tabela Admin
- Header escuro com letras maiúsculas
- Linhas com hover sutil
- Badges de status coloridos
- Ações com ícones SVG

---

## ✨ 6. Animações e Microinterações

```css
/* Transições suaves em tudo */
--transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

/* Efeitos específicos */

/* 1. Fade-in em cada step */
.step-enter {
    animation: fadeInUp 0.4s ease forwards;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 2. Botão CTA com brilho */
.btn-cta {
    position: relative;
    overflow: hidden;
}
.btn-cta::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(212,175,55,0.2) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.3s;
}
.btn-cta:hover::after {
    opacity: 1;
}

/* 3. Check animado no ticket */
.check-animated {
    animation: scaleCheck 0.5s ease;
}
@keyframes scaleCheck {
    0% { transform: scale(0); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
}

/* 4. Spinner minimalista com cor dourada */
.spinner {
    border-color: var(--bg-elevated);
    border-top-color: var(--gold);
}

/* 5. Skeleton loading para cards de serviço */
```

---

## 🗂️ 7. Estrutura de Arquivos (Refatoração de Frontend)

Atualmente o CSS e JS estão em arquivos únicos. A sugestão abaixo é **apenas para referência de organização** — não precisa ser implementada agora:

```
frontend/
├── index.html                    # Home
├── agendamento.html              # Agendamento (3 etapas)
├── admin.html                    # Painel Admin
├── meu-agendamento.html          # Consulta por hash
│
├── css/
│   ├── variables.css             # Paleta de cores, tipografia
│   ├── reset.css                 # Reset e base
│   ├── layout.css                # Grid, container, navbar
│   ├── components.css            # Cards, botões, modais
│   └── responsive.css            # Media queries
│
├── js/
│   ├── api.js                    # API client
│   ├── agendamento.js            # Lógica do booking
│   ├── admin.js                  # Lógica do admin
│   └── utils.js                  # Formatação, helpers
│
├── img/
│   ├── logo.svg                  # Logo vetorizado
│   ├── favicon.svg               # Favicon
│   └── icons/                    # Ícones SVG
│
└── assets/
    └── fonts/                    # Fontes locais (opcional)
```

---

## 🚀 8. Plano de Implementação do Design

### Fase 1 — Base (Prioridade Alta)
- [ ] Inserir logo real na navbar (substituir "✂️ Barbearia")
- [ ] Aplicar paleta de cores refinada (`--gold` em vez de `--accent: #C8A97E`)
- [ ] Refinar tipografia (Playfair Display para títulos)
- [ ] Hero section com logo e assinatura do Anderson

### Fase 2 — Componentes (Prioridade Média)
- [ ] Substituir emojis por ícones SVG consistentes
- [ ] Melhorar step indicator com animações
- [ ] Ticket com borda dourada e "Deus é Fiel"
- [ ] Botão CTA com efeito de brilho

### Fase 3 — Polimento (Prioridade Baixa)
- [ ] Animações de transição entre steps
- [ ] Skeleton loading
- [ ] Favicon personalizado
- [ ] Responsivo refinado (hamburger menu)

---

## 🎨 9. Aplicação Imediata no Código Atual

Se for aplicar agora sem quebrar nada, siga esta ordem:

### 9.1 No `style.css` atual
```css
:root {
    /* Manter as variáveis atuais, MAS adicionar: */
    --gold: #D4AF37;
    --gold-hover: #C49B2C;
    --gold-soft: rgba(212, 175, 55, 0.15);
    --border-gold: rgba(212, 175, 55, 0.3);
    --font-display: 'Playfair Display', 'Georgia', serif;
}
```

### 9.2 No `index.html`
- Colocar `<img src="/img/logo.png" alt="BarbeCity Jaraguá">` na navbar
- Adicionar o logo grande no hero
- Adicionar "Anderson Barbeiro" e "Deus é Fiel"

### 9.3 No `agendamento.html`
- Trocar header do ticket para "🟥 BARCECITY JARAGUÁ"
- Adicionar "Deus é Fiel" no rodapé do ticket
- Adicionar borda dourada no ticket

### 9.4 No `meu-agendamento.html`
- Manter o design atual, aplicar as mesmas cores

### 9.5 No `admin.html`
- Adicionar logo pequeno no header
- Manter funcional, refinar visual depois

---

## 📋 10. Checklist de Design x Funcionalidades

| # | Funcionalidade | Status Design | Refinamento |
|---|---------------|---------------|-------------|
| RF1 | Seleção de serviço | ✅ Cards implementados | Adicionar ícones SVG |
| RF2 | Calendário dinâmico | ✅ 14 dias gerados | Melhorar visual dos dias |
| RF3 | Slots com intervalo 30min | ✅ Algoritmo implementado | ✅ Ok |
| RF4 | Validação de conflitos | ✅ Implementada | ✅ Ok |
| RF5 | Link WhatsApp | ✅ Gerado | ✅ Ok |
| RF6 | Mensagem formatada | ✅ Personalizada | ✅ Ok |
| RF7 | Campo observações | ✅ Opcional | ✅ Ok |
| RF8 | Ticket com código | ✅ Hash + download | Adicionar logo + frase |
| RF9 | Download do ticket | ✅ html2canvas | Melhorar layout |
| RF10 | Painel Admin | ✅ CRUD completo | Refinar visual |
| RF11 | Consulta por hash | ✅ Funcional | ✅ Ok |
| RF12 | Bloqueio de datas | ✅ Implementado | ✅ Ok |
| - | "Deus é Fiel" | ❌ Ausente | Adicionar no footer + ticket |
| - | Logo BarbeCity | ❌ Ausente | Inserir na navbar + hero |

---

## 🖼️ 11. Referência Visual do Logo

O logo `logo.jpeg` está localizado em `barbearia-app/imagem/logo.jpeg`.

**Para usar no frontend:**
1. Copiar `logo.jpeg` para `barbearia-app/frontend/img/logo.png` (convertido para PNG)
2. Referenciar como `<img src="/img/logo.png" alt="BarbeCity Jaraguá">`
3. No CSS, o logo pode ter altura fixa de 40px na navbar e 200px no hero

**Cores extraídas do logo para referência:**
- Vermelho Bordô: `#8B0000` (primária)
- Dourado: `#D4AF37` (destaque)
- Fundo escuro: `#1A1A1A` (superfície)
- Texto claro: `#F5F5F5` (primário)

---

> **Conclusão:** O projeto atual tem uma base sólida e funcional. O refinamento de design proposto neste documento visa elevar a identidade visual para alinhar com o logo **BarbeCity Jaraguá**, criando uma experiência premium, dark e industrial que reflete a personalidade do Anderson e seu trabalho.
