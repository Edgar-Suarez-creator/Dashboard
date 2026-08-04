import express from 'express';
import db from '../database/db.js';
import { verifyToken } from './auth.js';
import XLSX from 'xlsx';

const router = express.Router();

// Obtener datos para gráficas
router.get('/graficas', verifyToken, async (req, res) => {
  try {
    const { mes, año, hub, ods } = req.query;
    
    let query = 'SELECT * FROM jornadas WHERE 1=1';
    const params = [];

    if (año) {
      query += ' AND año = ?';
      params.push(año);
    }

    if (mes) {
      query += ' AND CAST(substr(fecha, 6, 2) AS INTEGER) = ?';
      params.push(mes);
    }

    if (hub) {
      query += ' AND hub = ?';
      params.push(hub);
    }

    if (ods) {
      query += ' AND ods = ?';
      params.push(ods);
    }

    const jornadas = await db.all(query, params);

    // Gráfica por HUB
    const porHub = {};
    jornadas.forEach(j => {
      if (j.hub) {
        porHub[j.hub] = (porHub[j.hub] || 0) + j.horas;
      }
    });

    // Gráfica por ODS
    const porODS = {};
    jornadas.forEach(j => {
      if (j.ods) {
        porODS[j.ods] = (porODS[j.ods] || 0) + j.horas;
      }
    });

    // Gráfica por disciplina
    const porDisciplina = {};
    jornadas.forEach(j => {
      porDisciplina[j.disciplina] = (porDisciplina[j.disciplina] || 0) + j.horas;
    });

    // Gráfica por actividad
    const porActividad = {};
    jornadas.forEach(j => {
      porActividad[j.actividad] = (porActividad[j.actividad] || 0) + j.horas;
    });

    // Gráfica por proyecto
    const porProyecto = {};
    jornadas.forEach(j => {
      if (j.proyecto) {
        porProyecto[j.proyecto] = (porProyecto[j.proyecto] || 0) + j.horas;
      }
    });

    res.json({
      porHub: Object.entries(porHub).map(([name, value]) => ({ name, value })),
      porODS: Object.entries(porODS).map(([name, value]) => ({ name, value })),
      porDisciplina: Object.entries(porDisciplina).map(([name, value]) => ({ name, value })),
      porActividad: Object.entries(porActividad).map(([name, value]) => ({ name, value })),
      porProyecto: Object.entries(porProyecto).map(([name, value]) => ({ name, value })),
    });
  } catch (error) {
    console.error('Error al obtener datos de gráficas:', error);
    res.status(500).json({ error: 'Error al obtener datos de gráficas' });
  }
});

// Detalle de personal
router.get('/detalle-personal', verifyToken, async (req, res) => {
  try {
    const { mes, año } = req.query;
    
    let query = `
      SELECT 
        u.nombre || ' ' || u.apellido as nombre_completo,
        u.cargo,
        u.disciplina,
        SUM(j.horas) as total_horas,
        COUNT(j.id) as total_registros
      FROM usuarios u
      LEFT JOIN jornadas j ON u.id = j.usuario_id
      WHERE 1=1
    `;
    const params = [];

    if (año) {
      query += ' AND j.año = ?';
      params.push(año);
    }

    if (mes) {
      query += ' AND CAST(substr(j.fecha, 6, 2) AS INTEGER) = ?';
      params.push(mes);
    }

    query += ' GROUP BY u.id, u.nombre, u.apellido, u.cargo, u.disciplina ORDER BY total_horas DESC';

    const detalle = await db.all(query, params);

    // Abreviar cargos
    const abreviarCargo = (cargo) => {
      const abreviaciones = {
        'Técnico mecánico rotativo': 'Tec. Mec. Rot.',
        'Técnico mecánico estático': 'Tec. Mec. Est.',
        'Técnico electricista': 'Tec. Elec.',
        'Técnico de instrumentación': 'Tec. Inst.',
        'Técnico de caracterización': 'Tec. Carac.',
        'Ingeniero civil': 'Ing. Civ.',
        'Ingeniero mecánico': 'Ing. Mec.',
        'Ingeniero electricista': 'Ing. Elec.',
        'Ingeniero de instrumentación': 'Ing. Inst.',
        'Ingeniero de planeación': 'Ing. Plan.',
        'Ingeniero certificador': 'Ing. Cert.',
      };
      return abreviaciones[cargo] || cargo;
    };

    const detalleAbreviado = detalle.map(item => ({
      ...item,
      cargo_abreviado: abreviarCargo(item.cargo),
    }));

    res.json(detalleAbreviado);
  } catch (error) {
    console.error('Error al obtener detalle de personal:', error);
    res.status(500).json({ error: 'Error al obtener detalle de personal' });
  }
});

// Informe mensual
router.get('/informe-mensual', verifyToken, async (req, res) => {
  try {
    const { mes, año } = req.query;

    if (!mes || !año) {
      return res.status(400).json({ error: 'Mes y año son requeridos' });
    }

    const jornadas = await db.all(
      `SELECT * FROM jornadas 
       WHERE año = ? AND CAST(substr(fecha, 6, 2) AS INTEGER) = ?`,
      [año, mes]
    );

    const totalHoras = jornadas.reduce((sum, j) => sum + j.horas, 0);
    const totalExtras = jornadas.reduce((sum, j) => sum + (j.extras || 0), 0);
    const totalRegistros = jornadas.length;
    const totalUsuarios = new Set(jornadas.map(j => j.usuario_id)).size;

    // Por disciplina
    const porDisciplina = {};
    jornadas.forEach(j => {
      porDisciplina[j.disciplina] = (porDisciplina[j.disciplina] || 0) + j.horas;
    });

    // Por actividad
    const porActividad = {};
    jornadas.forEach(j => {
      porActividad[j.actividad] = (porActividad[j.actividad] || 0) + j.horas;
    });

    // Calcular porcentajes
    const porcentajeDisciplina = Object.entries(porDisciplina).map(([name, horas]) => ({
      name,
      horas,
      porcentaje: ((horas / totalHoras) * 100).toFixed(2)
    }));

    const porcentajeActividad = Object.entries(porActividad).map(([name, horas]) => ({
      name,
      horas,
      porcentaje: ((horas / totalHoras) * 100).toFixed(2)
    }));

    res.json({
      resumen: {
        mes: parseInt(mes),
        año: parseInt(año),
        totalHoras,
        totalExtras,
        totalRegistros,
        totalUsuarios,
      },
      porDisciplina: porcentajeDisciplina,
      porActividad: porcentajeActividad,
    });
  } catch (error) {
    console.error('Error al generar informe mensual:', error);
    res.status(500).json({ error: 'Error al generar informe mensual' });
  }
});

// Exportar a Excel
router.get('/exportar-excel', verifyToken, async (req, res) => {
  try {
    const { mes, año } = req.query;
    
    let query = 'SELECT * FROM jornadas WHERE 1=1';
    const params = [];

    if (año) {
      query += ' AND año = ?';
      params.push(año);
    }

    if (mes) {
      query += ' AND CAST(substr(fecha, 6, 2) AS INTEGER) = ?';
      params.push(mes);
    }

    const jornadas = await db.all(query, params);

    // Preparar datos para Excel
    const datos = jornadas.map(j => ({
      'ID': j.id,
      'Usuario': j.usuario,
      'Fecha': j.fecha,
      'Semana': j.semana,
      'Año': j.año,
      'HUB': j.hub || '',
      'ODS': j.ods || '',
      'Proyecto': j.proyecto || '',
      'Cargo': j.cargo,
      'Disciplina': j.disciplina,
      'Actividad': j.actividad,
      'Descripción': j.descripcion || '',
      'Horas': j.horas,
      'Jornada': j.jornada,
      'Extras': j.extras || 0,
    }));

    const worksheet = XLSX.utils.json_to_sheet(datos);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Jornadas');

    const excelBuffer = XLSX.write(workbook, { type: 'buffer', bookType: 'xlsx' });

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename=horas_hombre_${año || 'todos'}_${mes || 'todos'}.xlsx`);
    res.send(excelBuffer);
  } catch (error) {
    console.error('Error al exportar a Excel:', error);
    res.status(500).json({ error: 'Error al exportar a Excel' });
  }
});

export default router;



