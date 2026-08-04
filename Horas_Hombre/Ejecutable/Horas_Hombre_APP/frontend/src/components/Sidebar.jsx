import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  FaHome, 
  FaClock, 
  FaChartBar, 
  FaSignOutAlt,
  FaUser
} from 'react-icons/fa';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { path: '/dashboard', icon: FaHome, label: 'Dashboard' },
    { path: '/registrar-jornada', icon: FaClock, label: 'Registrar Jornada' },
    { path: '/reportes', icon: FaChartBar, label: 'Reportes' },
  ];

  return (
    <motion.div
      initial={{ x: -100 }}
      animate={{ x: 0 }}
      className="bg-white shadow-lg h-screen w-64 fixed left-0 top-0 flex flex-col"
    >
      <div className="p-6 border-b">
        <h1 className="text-xl font-bold text-primary-600">Horas Hombre</h1>
        <p className="text-sm text-gray-600 mt-1">Sistema de Control</p>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-2 px-4">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-100 text-primary-700 font-semibold'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="text-xl" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t">
        <div className="flex items-center space-x-3 mb-4 px-4">
          <div className="bg-primary-100 rounded-full p-2">
            <FaUser className="text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-800 truncate">
              {user?.nombre} {user?.apellido}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.cargo}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
        >
          <FaSignOutAlt />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </motion.div>
  );
};

export default Sidebar;





