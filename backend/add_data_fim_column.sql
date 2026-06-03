-- Script SQL para adicionar a coluna data_fim na tabela bloqueios
-- Execute este script no seu banco de dados PostgreSQL do Vercel

-- Verificar se a coluna já existe
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'bloqueios' AND column_name = 'data_fim';

-- Se não existir, adicionar a coluna
ALTER TABLE bloqueios ADD COLUMN IF NOT EXISTS data_fim TEXT DEFAULT '';

-- Verificar se a coluna foi adicionada corretamente
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'bloqueios' AND column_name = 'data_fim';