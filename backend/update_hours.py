
import os
from database import get_connection

def update_horarios():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Atualizando horários de funcionamento...")
    
    # Domingo
    cursor.execute("UPDATE configuracao_horarios SET abertura = '08:00', fechamento = '18:00', ativo = 1 WHERE dia_semana = 0")
    
    # Segunda a Sábado
    for dia in range(1, 7):
        cursor.execute("UPDATE configuracao_horarios SET abertura = '08:00', fechamento = '21:30', ativo = 1 WHERE dia_semana = %s", (dia,))
    
    conn.commit()
    conn.close()
    print("✅ Horários atualizados com sucesso!")

if __name__ == '__main__':
    update_horarios()
