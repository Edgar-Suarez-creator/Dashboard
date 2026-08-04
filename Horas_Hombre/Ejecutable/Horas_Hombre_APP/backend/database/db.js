import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dbPath = path.join(__dirname, 'horas_hombre.db');
const db = new sqlite3.Database(dbPath);

// Promisificar métodos de la base de datos
db.run = promisify(db.run.bind(db));
db.get = promisify(db.get.bind(db));
db.all = promisify(db.all.bind(db));

export const initDatabase = () => {
  // Tabla de usuarios
  db.run(`
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL,
      apellido TEXT NOT NULL,
      cedula TEXT UNIQUE NOT NULL,
      cargo TEXT NOT NULL,
      disciplina TEXT NOT NULL,
      rol TEXT NOT NULL,
      usuario TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Tabla de jornadas
  db.run(`
    CREATE TABLE IF NOT EXISTS jornadas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario_id INTEGER NOT NULL,
      usuario TEXT NOT NULL,
      fecha TEXT NOT NULL,
      semana INTEGER NOT NULL,
      año INTEGER NOT NULL,
      hub TEXT,
      ods TEXT,
      proyecto TEXT,
      cargo TEXT NOT NULL,
      disciplina TEXT NOT NULL,
      actividad TEXT NOT NULL,
      descripcion TEXT,
      horas REAL NOT NULL,
      jornada TEXT NOT NULL,
      extras REAL DEFAULT 0,
      imagen TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
  `);

  // Tabla de hubs y ods
  db.run(`
    CREATE TABLE IF NOT EXISTS hubs_ods (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      hub TEXT NOT NULL,
      ods TEXT NOT NULL,
      UNIQUE(hub, ods)
    )
  `);

  // Insertar datos iniciales de HUBs y ODS
  const hubsODS = [
    { hub: 'ANDINA ORIENTE', ods: ['ODS 005', 'ODS 071', 'ODS 081'] },
    { hub: 'CENTRAL', ods: ['ODS 010', 'ODS 020', 'ODS 030'] },
    { hub: 'CORPORATIVO Y NUEVAS ENERGIAS', ods: ['ODS 001', 'ODS 002', 'ODS 003'] },
    { hub: 'DOWNSTREAM', ods: ['ODS 100', 'ODS 101', 'ODS 102'] },
    { hub: 'ORINOQUIA', ods: ['ODS 200', 'ODS 201', 'ODS 202'] },
    { hub: 'PIEDEMONTE', ods: ['ODS 300', 'ODS 301', 'ODS 302'] },
  ];

  hubsODS.forEach(({ hub, ods }) => {
    ods.forEach(odsItem => {
      db.run(
        'INSERT OR IGNORE INTO hubs_ods (hub, ods) VALUES (?, ?)',
        [hub, odsItem]
      );
    });
  });

  console.log('✅ Base de datos inicializada correctamente');
};

export default db;



