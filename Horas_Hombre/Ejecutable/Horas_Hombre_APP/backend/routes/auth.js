import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import db from '../database/db.js';

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'tu_secreto_super_seguro_aqui';

// Registro de usuario
router.post('/register', async (req, res) => {
  try {
    const { nombre, apellido, cedula, cargo, disciplina, rol, usuario, password, confirmPassword } = req.body;

    // Validaciones
    if (!nombre || !apellido || !cedula || !cargo || !disciplina || !rol || !usuario || !password) {
      return res.status(400).json({ error: 'Todos los campos son requeridos' });
    }

    if (password !== confirmPassword) {
      return res.status(400).json({ error: 'Las contraseñas no coinciden' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: 'La contraseña debe tener al menos 6 caracteres' });
    }

    // Verificar si el usuario ya existe
    const existingUser = await db.get('SELECT * FROM usuarios WHERE usuario = ? OR cedula = ?', [usuario, cedula]);
    if (existingUser) {
      return res.status(400).json({ error: 'El usuario o cédula ya está registrado' });
    }

    // Hash de la contraseña
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insertar usuario
    const result = await db.run(
      'INSERT INTO usuarios (nombre, apellido, cedula, cargo, disciplina, rol, usuario, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [nombre, apellido, cedula.replace(/\s/g, ''), cargo, disciplina, rol, usuario, hashedPassword]
    );

    res.status(201).json({ 
      message: 'Usuario registrado exitosamente',
      userId: result.lastID 
    });
  } catch (error) {
    console.error('Error en registro:', error);
    res.status(500).json({ error: 'Error al registrar usuario' });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { usuario, password } = req.body;

    if (!usuario || !password) {
      return res.status(400).json({ error: 'Usuario y contraseña son requeridos' });
    }

    // Buscar usuario
    const user = await db.get('SELECT * FROM usuarios WHERE usuario = ?', [usuario]);
    if (!user) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Verificar contraseña
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Obtener último registro del usuario
    const lastJornada = await db.get(
      'SELECT * FROM jornadas WHERE usuario_id = ? ORDER BY created_at DESC LIMIT 1',
      [user.id]
    );

    // Generar token JWT
    const token = jwt.sign(
      { userId: user.id, usuario: user.usuario },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        nombre: user.nombre,
        apellido: user.apellido,
        cedula: user.cedula,
        cargo: user.cargo,
        disciplina: user.disciplina,
        rol: user.rol,
        usuario: user.usuario,
      },
      lastJornada: lastJornada || null
    });
  } catch (error) {
    console.error('Error en login:', error);
    res.status(500).json({ error: 'Error al iniciar sesión' });
  }
});

// Recuperar contraseña
router.post('/forgot-password', async (req, res) => {
  try {
    const { cedula, usuario, newPassword } = req.body;

    if (!cedula || !usuario || !newPassword) {
      return res.status(400).json({ error: 'Todos los campos son requeridos' });
    }

    // Verificar usuario
    const user = await db.get('SELECT * FROM usuarios WHERE cedula = ? AND usuario = ?', [cedula.replace(/\s/g, ''), usuario]);
    if (!user) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    // Actualizar contraseña
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    await db.run('UPDATE usuarios SET password = ? WHERE id = ?', [hashedPassword, user.id]);

    res.json({ message: 'Contraseña actualizada exitosamente' });
  } catch (error) {
    console.error('Error en recuperación de contraseña:', error);
    res.status(500).json({ error: 'Error al recuperar contraseña' });
  }
});

// Middleware para verificar token
export const verifyToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Token no proporcionado' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.userId = decoded.userId;
    req.usuario = decoded.usuario;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Token inválido' });
  }
};

export default router;



