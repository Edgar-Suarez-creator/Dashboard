import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { FaTimes, FaMagic } from 'react-icons/fa';

const actividades = [
  'CAPACITACIONES Y TALLERES DE MADURACIÓN',
  'CARACTERIZACIÓN',
  'CATALOGACIÓN Y PLANES DE MTTO',
  'COMISIONAMIENTO',
  'DECOMISIONAMIENTO',
  'INFORMES',
  'PERSONAL TRANSVERSAL, LOGÍSTICO Y HSE',
  'PLANEACIÓN',
  'PRESERVACIÓN',
  'PRUEBAS FAT',
  'REUNIONES Y AUDITORÍAS',
  'TIEMPOS NO PRODUCTIVOS',
];

const ActividadModal = ({ onClose, onSelect, currentActividad, onDescripcionAI }) => {
  const [selectedActividades, setSelectedActividades] = useState(
    currentActividad ? [currentActividad] : []
  );
  const [descripcion, setDescripcion] = useState('');
  const [generatingAI, setGeneratingAI] = useState(false);

  const handleToggleActividad = (actividad) => {
    setSelectedActividades(prev => {
      if (prev.includes(actividad)) {
        return prev.filter(a => a !== actividad);
      } else {
        // Solo permitir una actividad seleccionada
        return [actividad];
      }
    });
  };

  const handleSubmit = () => {
    if (selectedActividades.length === 0) {
      toast.error('Por favor selecciona al menos una actividad');
      return;
    }
    onSelect(selectedActividades[0]);
    if (descripcion && onDescripcionAI) {
      onDescripcionAI(descripcion);
    }
  };

  const generateAIDescription = async () => {
    if (selectedActividades.length === 0) {
      toast.error('Primero selecciona una actividad');
      return;
    }

    setGeneratingAI(true);
    try {
      // Nota: Para usar Gemini API, necesitarías configurar el backend
      // Por ahora, generamos una descripción básica
      const actividad = selectedActividades[0];
      const descripcionGenerada = `Actividades realizadas relacionadas con ${actividad.toLowerCase()}. ` +
        `Se trabajó en las tareas asignadas correspondientes a esta área durante la jornada.`;
      
      setDescripcion(descripcionGenerada);
      toast.success('Descripción generada');
    } catch (error) {
      toast.error('Error al generar descripción con IA');
    } finally {
      setGeneratingAI(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-lg max-w-3xl w-full p-6 relative max-h-[90vh] overflow-y-auto"
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          >
            <FaTimes className="text-xl" />
          </button>

          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Seleccionar Actividad General
          </h2>

          <div className="space-y-6">
            <div>
              <label className="label-field mb-3 block">Selecciona una actividad:</label>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {actividades.map(actividad => (
                  <label
                    key={actividad}
                    className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedActividades.includes(actividad)}
                      onChange={() => handleToggleActividad(actividad)}
                      className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <span className="text-gray-700">{actividad}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="label-field mb-0">Descripción Diaria (Opcional)</label>
                <button
                  type="button"
                  onClick={generateAIDescription}
                  disabled={generatingAI || selectedActividades.length === 0}
                  className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50"
                >
                  <FaMagic />
                  <span>{generatingAI ? 'Generando...' : 'Generar con IA'}</span>
                </button>
              </div>
              <textarea
                className="input-field"
                rows="4"
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                placeholder="Describe las actividades realizadas o usa IA para generar automáticamente..."
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
                type="button"
                onClick={handleSubmit}
                className="flex-1 btn-primary"
              >
                Confirmar
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ActividadModal;


