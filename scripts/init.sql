-- Garante que o banco existe com charset correto
CREATE DATABASE IF NOT EXISTS personal_finance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Garante permissões do usuário
GRANT ALL PRIVILEGES ON personal_finance.* TO 'financa'@'%';
FLUSH PRIVILEGES;
