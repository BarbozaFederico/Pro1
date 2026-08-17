PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('ADMIN', 'ENCARGADO', 'PROFESIONAL', 'USER')),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fichas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    profesional_id INTEGER NOT NULL,
    diagnostico TEXT,
    observaciones TEXT,
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES usuarios(id),
    FOREIGN KEY (profesional_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS planes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ficha_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'FINALIZADO', 'CANCELADO')),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ficha_id) REFERENCES fichas(id)
);

CREATE TABLE IF NOT EXISTS ejercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS plan_ejercicios (
    plan_id INTEGER NOT NULL,
    ejercicio_id INTEGER NOT NULL,
    series INTEGER,
    repeticiones INTEGER,
    observaciones TEXT,
    PRIMARY KEY (plan_id, ejercicio_id),
    FOREIGN KEY (plan_id) REFERENCES planes(id) ON DELETE CASCADE,
    FOREIGN KEY (ejercicio_id) REFERENCES ejercicios(id)
);

CREATE TABLE IF NOT EXISTS notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    leida INTEGER NOT NULL DEFAULT 0 CHECK (leida IN (0, 1)),
    creada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
