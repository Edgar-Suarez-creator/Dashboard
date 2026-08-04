# Control de Horas Hombre

Sistema web moderno y responsivo para el registro, visualización y análisis de horas trabajadas por usuario, disciplina, proyecto y actividades.

## 🚀 Tecnologías

### Frontend
- **React** + **Vite** - Framework y build tool
- **TailwindCSS** - Estilos y diseño responsivo
- **Recharts** - Gráficas interactivas
- **Framer Motion** - Animaciones suaves
- **React Router** - Navegación
- **Axios** - Cliente HTTP
- **React Hot Toast** - Notificaciones

### Backend
- **Node.js** + **Express** - Servidor y API
- **SQLite** - Base de datos
- **JWT** - Autenticación
- **Multer** - Manejo de archivos
- **Bcrypt** - Hash de contraseñas
- **XLSX** - Exportación a Excel

## 📋 Características

✅ **Autenticación completa**
- Registro de usuarios con validaciones
- Login seguro con JWT
- Recuperación de contraseña

✅ **Registro de jornadas**
- Registro diario con todos los campos
- Selección de HUB, ODS y Proyecto
- Selección de disciplina y actividad
- Descripción con opción de generación por IA
- Adjuntar imágenes
- Validación de horas (1-8h diarias)

✅ **Dashboard y reportes**
- Gráficas interactivas (circular y barras)
- Filtros por mes, año, HUB y ODS
- Detalle de personal con cargos abreviados
- Informe mensual dinámico
- Exportación a Excel

✅ **Diseño moderno**
- Interfaz responsiva (PC, tablet, móvil)
- Animaciones con Framer Motion
- Paleta de colores suaves
- Sidebar de navegación

## 🛠️ Instalación

### Prerrequisitos
- Node.js 18+ y npm

### Pasos

1. **Instalar dependencias**
```bash
npm run install:all
```

2. **Configurar variables de entorno**
```bash
cd backend
cp .env.example .env
# Editar .env y configurar JWT_SECRET
```

3. **Iniciar servidor de desarrollo**
```bash
npm run dev
```

Esto iniciará:
- Frontend en `http://localhost:3000`
- Backend en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
Horas_Hombre_APP/
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── context/        # Context API (Auth)
│   │   ├── pages/          # Páginas principales
│   │   ├── App.jsx         # Componente principal
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   └── package.json
├── backend/
│   ├── database/           # Configuración de BD
│   ├── routes/             # Rutas de la API
│   ├── uploads/            # Imágenes subidas
│   ├── server.js           # Servidor principal
│   └── package.json
└── package.json            # Scripts principales
```

## 🔐 Autenticación

El sistema usa JWT para autenticación. Los tokens se almacenan en localStorage y se envían en cada petición.

## 📊 Base de Datos

SQLite con las siguientes tablas:
- `usuarios` - Información de usuarios
- `jornadas` - Registros de jornadas diarias
- `hubs_ods` - Relación HUB-ODS

## 🎨 Disciplinas Disponibles

- Técnico mecánico rotativo
- Técnico mecánico estático
- Técnico electricista
- Técnico de instrumentación
- Técnico de caracterización
- Obrero, Ayudante
- Ingeniero (civil, mecánico, electricista, etc.)
- Practicante, Inspector, HSE
- Gerente, Coordinador, Administración

## 📈 HUBs Disponibles

- ANDINA ORIENTE
- CENTRAL
- CORPORATIVO Y NUEVAS ENERGIAS
- DOWNSTREAM
- ORINOQUIA
- PIEDEMONTE

## 🚧 Próximas Mejoras

- [ ] Integración completa con Gemini API para descripciones
- [ ] Exportación a PDF
- [ ] Notificaciones push
- [ ] Modo oscuro
- [ ] Dashboard con más métricas

## 📝 Licencia

Este proyecto es de uso interno.

