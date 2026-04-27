#!/usr/bin/env python3
"""
Script para atualizar a tabela bloqueios adicionando a coluna data_fim.
Execute este script uma vez para atualizar o banco de dados existente.
"""

import os
import sys
from database import get_connection

def atualizar_tabela_bloqueios():
    """Adiciona a coluna data_fim na tabela bloqueios se não existir."""
    print("🔧 Atualizando tabela bloqueios...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar se a coluna data_fim já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bloqueios' AND column_name = 'data_fim'
        """)
        
        coluna_existe = cursor.fetchone()
        
        if not coluna_existe:
            print("📋 Adicionando coluna 'data_fim' na tabela bloqueios...")
            
            # Adicionar a coluna data_fim
            cursor.execute("ALTER TABLE bloqueios ADD COLUMN data_fim TEXT DEFAULT ''")
            conn.commit()
            print("✅ Coluna 'data_fim' adicionada com sucesso!")
        else:
            print("✅ Coluna 'data_fim' já existe na tabela bloqueios.")
        
        conn.close()
        print("🎉 Atualização concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar tabela bloqueios: {e}")
        if conn:
            conn.close()
        sys.exit(1)

if __name__ == '__main__':
    atualizar_tabela_bloqueios()