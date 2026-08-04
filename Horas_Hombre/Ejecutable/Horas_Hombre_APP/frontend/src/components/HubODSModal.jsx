import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { FaTimes } from 'react-icons/fa';

const HubODSModal = ({ onClose, onSelect, currentHub, currentODS, currentProyecto }) => {
  const [hubs, setHubs] = useState([]);
  const [odsList, setODSList] = useState([]);
  const [selectedHub, setSelectedHub] = useState(currentHub || '');
  const [selectedODS, setSelectedODS] = useState(currentODS || '');
  const [proyecto, setProyecto] = useState(currentProyecto || '');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHubs();
  }, []);

  useEffect(() => {
    if (selectedHub) {
      loadODS(selectedHub);
    } else {
      setODSList([]);
    }
  }, [selectedHub]);

  const loadHubs = async () => {
    try {
      const response = await axios.get('/api/jornada/hubs');
      setHubs(response.data);
      if (currentHub && response.data.includes(currentHub)) {
        setSelectedHub(currentHub);
      }
    } catch (error) {
      toast.error('Error al cargar HUBs');
    } finally {
      setLoading(false);
    }
  };

  const loadODS = async (hub) => {
    try {
      const response = await axios.get(`/api/jornada/ods/${hub}`);
      setODSList(response.data);
      if (currentODS && response.data.includes(currentODS)) {
        setSelectedODS(currentODS);
      }
    } catch (error) {
      toast.error('Error al cargar ODS');
    }
  };

  const handleSubmit = () => {
    if (!selectedHub || !selectedODS) {
      toast.error('Por favor selecciona HUB y ODS');
      return;
    }
    onSelect(selectedHub, selectedODS, proyecto);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-lg max-w-2xl w-full p-6 relative max-h-[90vh] overflow-y-auto"
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          >
            <FaTimes className="text-xl" />
          </button>

          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Seleccionar HUB / ODS / Proyecto
          </h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <label className="label-field">HUB *</label>
                <select
                  className="input-field"
                  value={selectedHub}
                  onChange={(e) => {
                    setSelectedHub(e.target.value);
                    setSelectedODS('');
                  }}
                >
                  <option value="">Seleccione un HUB</option>
                  {hubs.map(hub => (
                    <option key={hub} value={hub}>{hub}</option>
                  ))}
                </select>
              </div>

              {selectedHub && (
                <div>
                  <label className="label-field">ODS *</label>
                  <select
                    className="input-field"
                    value={selectedODS}
                    onChange={(e) => setSelectedODS(e.target.value)}
                  >
                    <option value="">Seleccione un ODS</option>
                    {odsList.map(ods => (
                      <option key={ods} value={ods}>{ods}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="label-field">Proyecto</label>
                <input
                  type="text"
                  className="input-field"
                  value={proyecto}
                  onChange={(e) => setProyecto(e.target.value)}
                  placeholder="Ingresa el nombre del proyecto (opcional)"
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
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default HubODSModal;





