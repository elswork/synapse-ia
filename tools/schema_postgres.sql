-- Esquema SQL para PostgreSQL - Proyecto Anticitera

-- Tabla de Eventos
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agent TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT,
    metadata JSONB
);

-- Tabla de Objetivos
CREATE TABLE IF NOT EXISTS goals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agent TEXT NOT NULL,
    goal TEXT NOT NULL,
    status TEXT DEFAULT 'active'
);

-- Tabla de Ciudadanía
CREATE TABLE IF NOT EXISTS citizens (
    id SERIAL PRIMARY KEY,
    alias TEXT UNIQUE NOT NULL,
    role TEXT DEFAULT 'Citizen',
    access_level INTEGER DEFAULT 1,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de TODOs (Tareas Plan X)
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    analysis TEXT,
    status TEXT DEFAULT 'pending'
);

-- Inserción de Arcontes iniciales
INSERT INTO citizens (alias, role, access_level) VALUES 
('Eloy', 'Arconte / COO', 10),
('Arquímedes', 'Arconte / CEO', 9),
('Athena', 'Arconte / Strategist', 9)
ON CONFLICT (alias) DO NOTHING;
