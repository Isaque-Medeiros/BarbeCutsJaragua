import urllib.request, json
import ssl

# Ignorar SSL para teste local
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar(data, servicoId, nome, servicoNome):
    print(f"=== {nome} ===")
    try:
        url = f'http://localhost:5000/api/horarios?data={data}&servicoId={servicoId}'
        resp = urllib.request.urlopen(url, timeout=5)
        data_json = json.loads(resp.read())
        hf = data_json['horarioFuncionamento']
        print(f"  Aberto: {hf['abertura']} - Fechado: {hf['fechamento']}")
        slots = data_json['slotsDisponiveis']
        print(f"  Total slots: {len(slots)}")
        if slots:
            print(f"  Primeiro: {slots[0]['horaInicio']} - {slots[0]['horaFim']}")
            print(f"  Ultimo:   {slots[-1]['horaInicio']} - {slots[-1]['horaFim']}")
        else:
            print("  SEM SLOTS!")
    except Exception as e:
        print(f"  ERRO: {e}")
    print()

# Sábado (06/06/2026) - 09-20
testar('2026-06-06', 1, 'SABADO - Corte (30min)', 'Corte')
testar('2026-06-06', 2, 'SABADO - Barba (20min)', 'Barba')
testar('2026-06-06', 3, 'SABADO - Sobrancelha (15min)', 'Sobrancelha')

# Terça (02/06/2026) - 13-20
testar('2026-06-02', 1, 'TERCA - Corte (30min)', 'Corte')
testar('2026-06-02', 2, 'TERCA - Barba (20min)', 'Barba')

# Domingo (07/06/2026) - 09-20
testar('2026-06-07', 3, 'DOMINGO - Sobrancelha (15min)', 'Sobrancelha')

# Quarta (03/06/2026) - 13-20
testar('2026-06-03', 5, 'QUARTA - Luzes (70min)', 'Luzes')
