import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FaUserPlus, FaSignInAlt, FaClock } from 'react-icons/fa';

const Welcome = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl w-full"
      >
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-block mb-6"
          >
            <FaClock className="text-white text-6xl md:text-8xl" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-4xl md:text-6xl font-bold text-white mb-4"
          >
            Control de Horas Hombre
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-xl md:text-2xl text-primary-100"
          >
            Sistema de registro y análisis de horas trabajadas
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link to="/register">
              <div className="card bg-white hover:shadow-2xl transition-shadow duration-300 cursor-pointer">
                <div className="flex flex-col items-center text-center">
                  <div className="bg-primary-100 rounded-full p-4 mb-4">
                    <FaUserPlus className="text-primary-600 text-3xl" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    Registrar Usuario
                  </h2>
                  <p className="text-gray-600">
                    Crea una nueva cuenta para comenzar a registrar tus horas trabajadas
                  </p>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link to="/login">
              <div className="card bg-white hover:shadow-2xl transition-shadow duration-300 cursor-pointer">
                <div className="flex flex-col items-center text-center">
                  <div className="bg-secondary-100 rounded-full p-4 mb-4">
                    <FaSignInAlt className="text-secondary-600 text-3xl" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    Iniciar Sesión
                  </h2>
                  <p className="text-gray-600">
                    Accede a tu cuenta para registrar y visualizar tus jornadas
                  </p>
                </div>
              </div>
            </Link>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Welcome;





