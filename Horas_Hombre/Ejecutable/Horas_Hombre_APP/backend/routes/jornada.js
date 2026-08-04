import express from 'express';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import db from '../database/db.js';
import { verifyToken } from './auth.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

// Configurar multer para subir imágenes
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '../uploads'));
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'jornada-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Solo se permiten imágenes (JPEG, JPG, PNG, GIF)'));
    }
  }
});

// Obtener información del usuario
router.get('/user-info', verifyToken, async (req, res) => {
  try {
    const user = await db.get('SELECT * FROM usuarios WHERE id = ?', [req.userId]);
    if (!user) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    // Obtener último registro del día
    const today = new Date().toISOString().split('T')[0];
    const lastJornada = await db.get(
      'SELECT * FROM jornadas WHERE usuario_id = ? AND fecha = ? ORDER BY created_at DESC LIMIT 1',
      [req.userId, today]
    );

    res.json({
      user: {
        cargo: user.cargo,
        disciplina: user.disciplina,
        hub: lastJornada?.hub || null,
        ods: lastJornada?.ods || null,
        proyecto: lastJornada?.proyecto || null,
      },
      hasJornadaToday: !!lastJornada
    });
  } catch (error) {
    console.error('Error al obtener info del usuario:', error);
    res.status(500).json({ error: 'Error al obtener información del usuario' });
  }
});

// Obtener HUBs y ODS
router.get('/hubs', async (req, res) => {
  try {
    const hubs = await db.all('SELECT DISTINCT hub FROM hubs_ods ORDER BY hub');
    res.json(hubs.map(h => h.hub));
  } catch (error) {
    console.error('Error al obtener HUBs:', error);
    res.status(500).json({ error: 'Error al obtener HUBs' });
  }
});

router.get('/ods/:hub', async (req, res) => {
  try {
    const { hub } = req.params;
    const ods = await db.all('SELECT ods FROM hubs_ods WHERE hub = ? ORDER BY ods', [hub]);
    res.json(ods.map(o => o.ods));
  } catch (error) {
    console.error('Error al obtener ODS:', error);
    res.status(500).json({ error: 'Error al obtener ODS' });
  }
});

// Registrar jornada
router.post('/registrar', verifyToken, upload.single('imagen'), async (req, res) => {
  try {
    const {
      hub,
      ods,
      proyecto,
      cargo,
      disciplina,
      actividad,
      descripcion,
      horas,
      jornada,
      extras
    } = req.body;

    // Validaciones
    if (!cargo || !disciplina || !actividad || !horas || !jornada) {
      return res.status(400).json({ error: 'Campos requeridos faltantes' });
    }

    const horasNum = parseFloat(horas);
    const extrasNum = parseFloat(extras || 0);

    if (horasNum <= 0 || horasNum > 8) {
      return res.status(400).json({ error: 'Las horas deben estar entre 1 y 8' });
    }

    // Obtener fecha, semana y año
    const now = new Date();
    const fecha = now.toISOString().split('T')[0];
    const año = now.getFullYear();
    
    // Calcular semana del año
    const startOfYear = new Date(año, 0, 1);
    const days = Math.floor((now - startOfYear) / (24 * 60 * 60 * 1000));
    const semana = Math.ceil((days + startOfYear.getDay() + 1) / 7);

    // Obtener usuario
    const user = await db.get('SELECT * FROM usuarios WHERE id = ?', [req.userId]);

    // Insertar jornada
    const imagenPath = req.file ? `/uploads/${req.file.filename}` : null;

    await db.run(
      `INSERT INTO jornadas 
       (usuario_id, usuario, fecha, semana, año, hub, ods, proyecto, cargo, disciplina, actividad, descripcion, horas, jornada, extras, imagen)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        req.userId,
        user.usuario,
        fecha,
        semana,
        año,
        hub || null,
        ods || null,
        proyecto || null,
        cargo,
        disciplina,
        actividad,
        descripcion || null,
        horasNum,
        jornada,
        extrasNum,
        imagenPath
      ]
    );

    res.status(201).json({ message: 'Jornada registrada exitosamente' });
  } catch (error) {
    console.error('Error al registrar jornada:', error);
    res.status(500).json({ error: 'Error al registrar jornada' });
  }
});

// Obtener jornadas del usuario
router.get('/mis-jornadas', verifyToken, async (req, res) => {
  try {
    const jornadas = await db.all(
      'SELECT * FROM jornadas WHERE usuario_id = ? ORDER BY fecha DESC, created_at DESC',
      [req.userId]
    );
    res.json(jornadas);
  } catch (error) {
    console.error('Error al obtener jornadas:', error);
    res.status(500).json({ error: 'Error al obtener jornadas' });
  }
});

export default router;



