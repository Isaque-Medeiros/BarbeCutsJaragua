
import os
import sys
from database import get_connection

def update_horarios():
    """Atualiza os horários de funcionamento no banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("📋 Atualizando horários de funcionamento...")
        print("📅 Domingo: 08:00 - 18:00")
        print("📅 Segunda a Sábado: 08:00 - 21:30")
        
        # Verificar se a tabela existe e tem registros
        cursor.execute("SELECT COUNT(*) as total FROM configuracao_horarios")
        row = cursor.fetchone()
        total = row['total'] if hasattr(row, '__getitem__') else row[0]
        
        if total == 0:
            print("❌ Nenhum horário encontrado na tabela configuracao_horarios")
            print("ℹ️  Os horários padrão já foram definidos na criação do banco (database.py)")
            conn.close()
            return
        
        # Domingo (dia_semana = 0)
        cursor.execute("UPDATE configuracao_horarios SET abertura = '08:00', fechamento = '18:00', ativo = 1 WHERE dia_semana = 0")
        
        # Segunda a Sábado (dia_semana = 1 a 6)
        for dia in range(1, 7):
            cursor.execute("UPDATE configuracao_horarios SET abertura = '08:00', fechamento = '21:30', ativo = 1 WHERE dia_semana = %s", (dia,))
        
        conn.commit()
        
        # Verificar as atualizações
        cursor.execute("SELECT dia_semana, abertura, fechamento, ativo FROM configuracao_horarios ORDER BY dia_semana")
        horarios_atualizados = cursor.fetchall()
        
        print("\n✅ Horários atualizados com sucesso!")
        print("\n📊 Horários configurados:")
        for horario in horarios_atualizados:
            dia = horario['dia_semana'] if hasattr(horario, '__getitem__') else horario[0]
            abertura = horario['abertura'] if hasattr(horario, '__getitem__') else horario[1]
            fechamento = horario['fechamento'] if hasattr(horario, '__getitem__') else horario[2]
            ativo = horario['ativo'] if hasattr(horario, '__getitem__') else horario[3]
            
            dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
            status = "✅" if ativo else "❌"
            print(f"{status} {dias_semana[dia]}: {abertura} - {fechamento}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao atualizar horários: {e}")
        print(f"ℹ️  Tipo do erro: {type(e).__name__}")
        if 'conn' in locals() and conn:
            conn.close()
        sys.exit(1)

if __name__ == '__main__':
    update_horarios()
