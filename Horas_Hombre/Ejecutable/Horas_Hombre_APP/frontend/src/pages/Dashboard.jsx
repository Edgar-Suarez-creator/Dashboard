import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/Sidebar';
import { FaClock, FaCalendarAlt, FaChartLine } from 'react-icons/fa';
import axios from 'axios';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalHoras: 0,
    totalRegistros: 0,
    horasEsteMes: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/jornada/mis-jornadas');
      const jornadas = response.data;
      
      const totalHoras = jornadas.reduce((sum, j) => sum + j.horas, 0);
      const mesActual = new Date().getMonth() + 1;
      const añoActual = new Date().getFullYear();
      const horasEsteMes = jornadas
        .filter(j => {
          const fecha = new Date(j.fecha);
          return fecha.getMonth() + 1 === mesActual && fecha.getFullYear() === añoActual;
        })
        .reduce((sum, j) => sum + j.horas, 0);

      setStats({
        totalHoras,
        totalRegistros: jornadas.length,
        horasEsteMes,
      });
    } catch (error) {
      toast.error('Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 ml-64 p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Bienvenido, {user?.nombre}
            </h1>
            <p className="text-gray-600">
              {format(new Date(), "EEEE, d 'de' MMMM 'de' yyyy", { locale: es })}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-primary-100 text-sm mb-1">Total de Horas</p>
                  <p className="text-3xl font-bold">
                    {loading ? '...' : stats.totalHoras.toFixed(1)}
                  </p>
                </div>
                <FaClock className="text-4xl text-primary-200" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card bg-gradient-to-br from-secondary-500 to-secondary-600 text-white"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-secondary-100 text-sm mb-1">Horas Este Mes</p>
                  <p className="text-3xl font-bold">
                    {loading ? '...' : stats.horasEsteMes.toFixed(1)}
                  </p>
                </div>
                <FaCalendarAlt className="text-4xl text-secondary-200" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="card bg-gradient-to-br from-green-500 to-green-600 text-white"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm mb-1">Total Registros</p>
                  <p className="text-3xl font-bold">
                    {loading ? '...' : stats.totalRegistros}
                  </p>
                </div>
                <FaChartLine className="text-4xl text-green-200" />
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Información del Usuario
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Cargo</p>
                <p className="text-lg font-semibold text-gray-800">{user?.cargo}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Disciplina</p>
                <p className="text-lg font-semibold text-gray-800">{user?.disciplina}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Rol</p>
                <p className="text-lg font-semibold text-gray-800">{user?.rol}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Usuario</p>
                <p className="text-lg font-semibold text-gray-800">{user?.usuario}</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;





