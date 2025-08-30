-- Adiciona colunas de representante, estado e cidade na tabela usuarios
ALTER TABLE usuarios ADD COLUMN representante TEXT;
ALTER TABLE usuarios ADD COLUMN estado TEXT;
ALTER TABLE usuarios ADD COLUMN cidade TEXT;
