import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { FaUserPlus, FaArrowLeft } from 'react-icons/fa';

const disciplinas = [
  'Técnico mecánico rotativo',
  'Técnico mecánico estático',
  'Técnico electricista',
  'Técnico de instrumentación',
  'Técnico de caracterización',
  'Obrero',
  'Ayudante',
  'Ingeniero civil',
  'Ingeniero mecánico',
  'Ingeniero electricista',
  'Ingeniero de instrumentación',
  'Ingeniero de planeación',
  'Ingeniero certificador',
  'Practicante',
  'Inspector',
  'HSE',
  'Gerente',
  'Coordinador',
  'Administración',
];

const Register = () => {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    cedula: '',
    cargo: '',
    disciplina: '',
    rol: '',
    usuario: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'cedula' ? value.replace(/\s/g, '') : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones
    const camposRequeridos = ['nombre', 'apellido', 'cedula', 'cargo', 'disciplina', 'rol', 'usuario', 'password', 'confirmPassword'];
    const camposVacios = camposRequeridos.filter(campo => !formData[campo]);

    if (camposVacios.length > 0) {
      toast.error(`Por favor completa todos los campos. Faltan: ${camposVacios.join(', ')}`);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/auth/register', formData);
      toast.success('Usuario registrado exitosamente');
      navigate('/login');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al registrar usuario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        <div className="card">
          <Link
            to="/"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
          >
            <FaArrowLeft className="mr-2" />
            Volver al inicio
          </Link>

          <div className="text-center mb-8">
            <div className="bg-primary-100 rounded-full p-4 inline-block mb-4">
              <FaUserPlus className="text-primary-600 text-3xl" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Registrar Usuario
            </h1>
            <p className="text-gray-600">
              Completa todos los campos para crear tu cuenta
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="label-field">Nombre *</label>
                <input
                  type="text"
                  name="nombre"
                  className="input-field"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label className="label-field">Apellido *</label>
                <input
                  type="text"
                  name="apellido"
                  className="input-field"
                  value={formData.apellido}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div>
              <label className="label-field">Cédula (sin espacios) *</label>
              <input
                type="text"
                name="cedula"
                className="input-field"
                value={formData.cedula}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="label-field">Cargo *</label>
              <input
                type="text"
                name="cargo"
                className="input-field"
                value={formData.cargo}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="label-field">Disciplina *</label>
              <select
                name="disciplina"
                className="input-field"
                value={formData.disciplina}
                onChange={handleChange}
                required
              >
                <option value="">Seleccione una disciplina</option>
                {disciplinas.map(dis => (
                  <option key={dis} value={dis}>{dis}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="label-field">Rol *</label>
              <input
                type="text"
                name="rol"
                className="input-field"
                value={formData.rol}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="label-field">Usuario *</label>
              <input
                type="text"
                name="usuario"
                className="input-field"
                value={formData.usuario}
                onChange={handleChange}
                required
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="label-field">Contraseña *</label>
                <input
                  type="password"
                  name="password"
                  className="input-field"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label className="label-field">Confirmar Contraseña *</label>
                <input
                  type="password"
                  name="confirmPassword"
                  className="input-field"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Registrando...' : 'Registrar Usuario'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;





