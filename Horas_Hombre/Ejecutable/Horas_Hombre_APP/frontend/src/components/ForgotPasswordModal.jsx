import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { FaTimes } from 'react-icons/fa';

const ForgotPasswordModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    cedula: '',
    usuario: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'cedula' ? value.replace(/\s/g, '') : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.cedula || !formData.usuario || !formData.newPassword) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (formData.newPassword.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/auth/forgot-password', {
        cedula: formData.cedula,
        usuario: formData.usuario,
        newPassword: formData.newPassword,
      });
      toast.success('Contraseña actualizada exitosamente');
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al recuperar contraseña');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-lg max-w-md w-full p-6 relative"
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          >
            <FaTimes className="text-xl" />
          </button>

          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Recuperar Contraseña
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label-field">Cédula</label>
              <input
                type="text"
                name="cedula"
                className="input-field"
                value={formData.cedula}
                onChange={handleChange}
                placeholder="Ingresa tu cédula"
              />
            </div>

            <div>
              <label className="label-field">Usuario</label>
              <input
                type="text"
                name="usuario"
                className="input-field"
                value={formData.usuario}
                onChange={handleChange}
                placeholder="Ingresa tu usuario"
              />
            </div>

            <div>
              <label className="label-field">Nueva Contraseña</label>
              <input
                type="password"
                name="newPassword"
                className="input-field"
                value={formData.newPassword}
                onChange={handleChange}
                placeholder="Ingresa tu nueva contraseña"
              />
            </div>

            <div>
              <label className="label-field">Confirmar Nueva Contraseña</label>
              <input
                type="password"
                name="confirmPassword"
                className="input-field"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirma tu nueva contraseña"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 btn-primary disabled:opacity-50"
              >
                {loading ? 'Actualizando...' : 'Actualizar Contraseña'}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ForgotPasswordModal;





