import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';
import toast from 'react-hot-toast';
import { FaDownload, FaFileExcel, FaChartPie } from 'react-icons/fa';
import * as XLSX from 'xlsx';

const COLORS = ['#3b82f6', '#f97316', '#10b981', '#8b5cf6', '#ef4444', '#06b6d4', '#f59e0b'];

const Reportes = () => {
  const [filters, setFilters] = useState({
    mes: new Date().getMonth() + 1,
    año: new Date().getFullYear(),
    hub: '',
    ods: '',
  });
  const [graficas, setGraficas] = useState({
    porHub: [],
    porODS: [],
    porDisciplina: [],
    porActividad: [],
    porProyecto: [],
  });
  const [detallePersonal, setDetallePersonal] = useState([]);
  const [informeMensual, setInformeMensual] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hubs, setHubs] = useState([]);

  useEffect(() => {
    loadHubs();
  }, []);

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadHubs = async () => {
    try {
      const response = await axios.get('/api/jornada/hubs');
      setHubs(response.data);
    } catch (error) {
      console.error('Error al cargar HUBs:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [graficasRes, detalleRes, informeRes] = await Promise.all([
        axios.get('/api/reportes/graficas', { params: filters }),
        axios.get('/api/reportes/detalle-personal', { params: filters }),
        axios.get('/api/reportes/informe-mensual', { params: filters }),
      ]);

      setGraficas(graficasRes.data);
      setDetallePersonal(detalleRes.data);
      setInformeMensual(informeRes.data);
    } catch (error) {
      toast.error('Error al cargar datos de reportes');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const exportToExcel = async () => {
    try {
      const response = await axios.get('/api/reportes/exportar-excel', {
        params: filters,
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `horas_hombre_${filters.año}_${filters.mes || 'todos'}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Archivo Excel descargado');
    } catch (error) {
      toast.error('Error al exportar a Excel');
    }
  };

  const renderPieChart = (data, title) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          No hay datos disponibles
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderBarChart = (data, title) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          No hay datos disponibles
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    );
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
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Reportes y Gráficas
              </h1>
              <p className="text-gray-600">
                Visualiza y analiza las horas trabajadas
              </p>
            </div>
            <button
              onClick={exportToExcel}
              className="btn-primary flex items-center space-x-2"
            >
              <FaFileExcel />
              <span>Exportar Excel</span>
            </button>
          </div>

          {/* Filtros */}
          <div className="card mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Filtros</h2>
            <div className="grid md:grid-cols-4 gap-4">
              <div>
                <label className="label-field">Mes</label>
                <select
                  className="input-field"
                  value={filters.mes}
                  onChange={(e) => handleFilterChange('mes', e.target.value)}
                >
                  <option value="">Todos</option>
                  {Array.from({ length: 12 }, (_, i) => i + 1).map(mes => (
                    <option key={mes} value={mes}>{mes}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label-field">Año</label>
                <input
                  type="number"
                  className="input-field"
                  value={filters.año}
                  onChange={(e) => handleFilterChange('año', e.target.value)}
                  min="2020"
                  max="2100"
                />
              </div>
              <div>
                <label className="label-field">HUB</label>
                <select
                  className="input-field"
                  value={filters.hub}
                  onChange={(e) => handleFilterChange('hub', e.target.value)}
                >
                  <option value="">Todos</option>
                  {hubs.map(hub => (
                    <option key={hub} value={hub}>{hub}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label-field">ODS</label>
                <input
                  type="text"
                  className="input-field"
                  value={filters.ods}
                  onChange={(e) => handleFilterChange('ods', e.target.value)}
                  placeholder="Filtrar por ODS"
                />
              </div>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : (
            <>
              {/* Gráficas */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="card">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Por HUB</h3>
                  {renderPieChart(graficas.porHub, 'Por HUB')}
                </div>

                <div className="card">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Por ODS</h3>
                  {renderBarChart(graficas.porODS, 'Por ODS')}
                </div>

                <div className="card">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Por Disciplina</h3>
                  {renderPieChart(graficas.porDisciplina, 'Por Disciplina')}
                </div>

                <div className="card">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Por Actividad</h3>
                  {renderPieChart(graficas.porActividad, 'Por Actividad')}
                </div>

                <div className="card md:col-span-2">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">Por Proyecto</h3>
                  {renderPieChart(graficas.porProyecto, 'Por Proyecto')}
                </div>
              </div>

              {/* Detalle de Personal */}
              <div className="card mb-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Detalle de Personal
                </h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cargo</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Disciplina</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Horas</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Registros</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {detallePersonal.map((persona, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {persona.nombre_completo}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {persona.cargo_abreviado || persona.cargo}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {persona.disciplina}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {persona.total_horas?.toFixed(1) || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {persona.total_registros || 0}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Informe Mensual */}
              {informeMensual && (
                <div className="card">
                  <h2 className="text-xl font-bold text-gray-800 mb-4">
                    Informe Mensual - {informeMensual.resumen.mes}/{informeMensual.resumen.año}
                  </h2>
                  <div className="grid md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-primary-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Horas</p>
                      <p className="text-2xl font-bold text-primary-600">
                        {informeMensual.resumen.totalHoras.toFixed(1)}
                      </p>
                    </div>
                    <div className="bg-secondary-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Horas Extras</p>
                      <p className="text-2xl font-bold text-secondary-600">
                        {informeMensual.resumen.totalExtras.toFixed(1)}
                      </p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Registros</p>
                      <p className="text-2xl font-bold text-green-600">
                        {informeMensual.resumen.totalRegistros}
                      </p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Usuarios</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {informeMensual.resumen.totalUsuarios}
                      </p>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-gray-800 mb-3">Por Disciplina</h3>
                      <div className="space-y-2">
                        {informeMensual.porDisciplina.map((item, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-700">{item.name}</span>
                            <div className="text-right">
                              <span className="text-sm font-semibold text-gray-800">{item.horas.toFixed(1)}h</span>
                              <span className="text-xs text-gray-500 ml-2">({item.porcentaje}%)</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800 mb-3">Por Actividad</h3>
                      <div className="space-y-2">
                        {informeMensual.porActividad.map((item, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-700">{item.name}</span>
                            <div className="text-right">
                              <span className="text-sm font-semibold text-gray-800">{item.horas.toFixed(1)}h</span>
                              <span className="text-xs text-gray-500 ml-2">({item.porcentaje}%)</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Reportes;


