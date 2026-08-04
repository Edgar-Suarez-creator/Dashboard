import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/Sidebar';
import HubODSModal from '../components/HubODSModal';
import ActividadModal from '../components/ActividadModal';
import axios from 'axios';
import toast from 'react-hot-toast';
import { FaSave, FaCalendarAlt } from 'react-icons/fa';
import { getWeek, getYear } from 'date-fns';

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

const RegistrarJornada = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    cargo: '',
    disciplina: '',
    actividad: '',
    descripcion: '',
    horas: '',
    jornada: 'AM',
    extras: '',
    proyecto: '',
  });
  const [hub, setHub] = useState(null);
  const [ods, setODS] = useState(null);
  const [showHubModal, setShowHubModal] = useState(false);
  const [showActividadModal, setShowActividadModal] = useState(false);
  const [imagen, setImagen] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    loadUserInfo();
  }, []);

  useEffect(() => {
    if (userInfo) {
      setFormData(prev => ({
        ...prev,
        cargo: userInfo.cargo || user?.cargo || '',
        disciplina: userInfo.disciplina || user?.disciplina || '',
      }));
      if (userInfo.hub) setHub(userInfo.hub);
      if (userInfo.ods) setODS(userInfo.ods);
      if (userInfo.proyecto) setFormData(prev => ({ ...prev, proyecto: userInfo.proyecto }));
    }
  }, [userInfo, user]);

  const loadUserInfo = async () => {
    try {
      const response = await axios.get('/api/jornada/user-info');
      setUserInfo(response.data.user);
      if (response.data.hasJornadaToday) {
        setHub(response.data.user.hub);
        setODS(response.data.user.ods);
        setFormData(prev => ({ ...prev, proyecto: response.data.user.proyecto || '' }));
      }
    } catch (error) {
      console.error('Error al cargar info del usuario:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('La imagen no debe superar los 5MB');
        return;
      }
      setImagen(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('La imagen no debe superar los 5MB');
        return;
      }
      setImagen(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.cargo || !formData.disciplina || !formData.actividad || !formData.horas) {
      toast.error('Por favor completa todos los campos requeridos');
      return;
    }

    const horasNum = parseFloat(formData.horas);
    if (horasNum <= 0 || horasNum > 8) {
      toast.error('Las horas deben estar entre 1 y 8');
      return;
    }

    // Si no hay HUB/ODS seleccionados hoy, mostrar modal
    if (!hub || !ods) {
      setShowHubModal(true);
      return;
    }

    setLoading(true);
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('hub', hub);
      formDataToSend.append('ods', ods);
      formDataToSend.append('proyecto', formData.proyecto);
      formDataToSend.append('cargo', formData.cargo);
      formDataToSend.append('disciplina', formData.disciplina);
      formDataToSend.append('actividad', formData.actividad);
      formDataToSend.append('descripcion', formData.descripcion);
      formDataToSend.append('horas', formData.horas);
      formDataToSend.append('jornada', formData.jornada);
      formDataToSend.append('extras', formData.extras || '0');
      if (imagen) {
        formDataToSend.append('imagen', imagen);
      }

      await axios.post('/api/jornada/registrar', formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Jornada registrada exitosamente');
      
      // Reset form
      setFormData({
        cargo: formData.cargo,
        disciplina: formData.disciplina,
        actividad: '',
        descripcion: '',
        horas: '',
        jornada: 'AM',
        extras: '',
        proyecto: formData.proyecto,
      });
      setImagen(null);
      loadUserInfo();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al registrar jornada');
    } finally {
      setLoading(false);
    }
  };

  const handleHubODSSelect = (selectedHub, selectedODS, proyecto) => {
    setHub(selectedHub);
    setODS(selectedODS);
    if (proyecto) {
      setFormData(prev => ({ ...prev, proyecto }));
    }
    setShowHubModal(false);
  };

  const handleActividadSelect = (actividad) => {
    setFormData(prev => ({ ...prev, actividad }));
    setShowActividadModal(false);
  };

  const fecha = new Date().toISOString().split('T')[0];
  const semana = getWeek(new Date());
  const año = getYear(new Date());

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 ml-64 p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Registrar Jornada Diaria
            </h1>
            <div className="flex items-center space-x-4 text-gray-600">
              <div className="flex items-center">
                <FaCalendarAlt className="mr-2" />
                <span>Fecha: {fecha}</span>
              </div>
              <span>|</span>
              <span>Semana: {semana}</span>
              <span>|</span>
              <span>Año: {año}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="card space-y-6">
            {/* HUB y ODS */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="label-field">HUB</label>
                <button
                  type="button"
                  onClick={() => setShowHubModal(true)}
                  className="input-field text-left bg-white cursor-pointer hover:bg-gray-50"
                >
                  {hub || 'Seleccionar HUB'}
                </button>
              </div>
              <div>
                <label className="label-field">ODS</label>
                <button
                  type="button"
                  onClick={() => setShowHubModal(true)}
                  className="input-field text-left bg-white cursor-pointer hover:bg-gray-50"
                >
                  {ods || 'Seleccionar ODS'}
                </button>
              </div>
            </div>

            {/* Proyecto */}
            <div>
              <label className="label-field">Proyecto</label>
              <input
                type="text"
                name="proyecto"
                className="input-field"
                value={formData.proyecto}
                onChange={handleChange}
                placeholder="Ingresa el nombre del proyecto"
              />
            </div>

            {/* Cargo y Disciplina */}
            <div className="grid md:grid-cols-2 gap-4">
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
            </div>

            {/* Actividad */}
            <div>
              <label className="label-field">Actividad General *</label>
              <button
                type="button"
                onClick={() => setShowActividadModal(true)}
                className="input-field text-left bg-white cursor-pointer hover:bg-gray-50"
              >
                {formData.actividad || 'Seleccionar Actividad'}
              </button>
            </div>

            {/* Descripción */}
            <div>
              <label className="label-field">Descripción Diaria</label>
              <textarea
                name="descripcion"
                className="input-field"
                rows="4"
                value={formData.descripcion}
                onChange={handleChange}
                placeholder="Describe las actividades realizadas..."
              />
            </div>

            {/* Horas y Jornada */}
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="label-field">Horas Trabajadas (1-8h) *</label>
                <input
                  type="number"
                  name="horas"
                  className="input-field"
                  value={formData.horas}
                  onChange={handleChange}
                  min="1"
                  max="8"
                  step="0.5"
                  required
                />
              </div>
              <div>
                <label className="label-field">Jornada *</label>
                <select
                  name="jornada"
                  className="input-field"
                  value={formData.jornada}
                  onChange={handleChange}
                  required
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
              <div>
                <label className="label-field">Horas Extras</label>
                <input
                  type="number"
                  name="extras"
                  className="input-field"
                  value={formData.extras}
                  onChange={handleChange}
                  min="0"
                  step="0.5"
                  placeholder="0"
                />
              </div>
            </div>

            {/* Imagen */}
            <div>
              <label className="label-field">Adjuntar Imagen</label>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors"
              >
                {imagen ? (
                  <div className="space-y-2">
                    <img
                      src={URL.createObjectURL(imagen)}
                      alt="Preview"
                      className="max-h-48 mx-auto rounded-lg"
                    />
                    <p className="text-sm text-gray-600">{imagen.name}</p>
                    <button
                      type="button"
                      onClick={() => setImagen(null)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Eliminar imagen
                    </button>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Arrastra una imagen aquí o haz clic para seleccionar
                    </p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                      id="imagen-input"
                    />
                    <label
                      htmlFor="imagen-input"
                      className="btn-secondary inline-block cursor-pointer"
                    >
                      Insertar Imagen
                    </label>
                  </div>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <FaSave />
              <span>{loading ? 'Registrando...' : 'Registrar Jornada'}</span>
            </button>
          </form>
        </motion.div>
      </div>

      {showHubModal && (
        <HubODSModal
          onClose={() => setShowHubModal(false)}
          onSelect={handleHubODSSelect}
          currentHub={hub}
          currentODS={ods}
          currentProyecto={formData.proyecto}
        />
      )}

      {showActividadModal && (
        <ActividadModal
          onClose={() => setShowActividadModal(false)}
          onSelect={handleActividadSelect}
          currentActividad={formData.actividad}
          onDescripcionAI={(descripcion) => setFormData(prev => ({ ...prev, descripcion }))}
        />
      )}
    </div>
  );
};

export default RegistrarJornada;





