import urllib.request, json
from datetime import datetime

hoje = datetime.now().strftime('%Y-%m-%d')
agora = datetime.now().strftime('%H:%M')
print(f'Horario atual: {agora}')
print(f'Data de HOJE: {hoje}')
print()

try:
    resp = urllib.request.urlopen(f'http://localhost:5000/api/horarios?data={hoje}&servicoId=1', timeout=5)
    d = json.loads(resp.read())
    slots = d['slotsDisponiveis']
    print(f'Slots para Corte hoje: {len(slots)}')
    if slots:
        print(f'Primeiro: {slots[0]["horaInicio"]}')
        print(f'Ultimo: {slots[-1]["horaInicio"]}')
        print()
        print('Slots gerados:')
        for s in slots:
            print(f'  {s["horaInicio"]} - {s["horaFim"]}')
    else:
        print('Nenhum slot disponivel (ja passou do horario!)')
except Exception as e:
    print(f'ERRO: {e}')
