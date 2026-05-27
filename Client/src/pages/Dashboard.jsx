import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  fetchDashboardKPIs,
  fetchDashboardMap,
  fetchTopPrioritySites,
  fetchPortfolioOverview,
  fetchActivities,
  uploadKml
} from '../api';
import usePortfolioStore from '../store/usePortfolioStore';
import {
  UploadCloud,
  BarChart3,
  PieChart as PieIcon,
  ListFilter,
  Map as MapIcon,
  Loader2,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import Map from '../components/Map';
import { cn } from '../lib/utils';

const COLORS = {
  VL: '#fde047',
  L: '#fcd34d',
  M: '#fb923c',
  H: '#f87171',
  VH: '#dc2626'
};

export default function Dashboard() {
  const { setKPIs } = usePortfolioStore();
  const [showUpload, setShowUpload] = useState(false);
  const [activeToggle, setActiveToggle] = useState('impact'); // impact or dependency
  const navigate = useNavigate();

  // Queries
  const { data: kpis, isLoading: loadingKPIs } = useQuery({ queryKey: ['dashboard-kpis'], queryFn: fetchDashboardKPIs });
  const { data: mapData, isLoading: loadingMap } = useQuery({ queryKey: ['dashboard-map'], queryFn: fetchDashboardMap });
  const { data: topSites } = useQuery({ queryKey: ['top-priority-sites'], queryFn: fetchTopPrioritySites });
  const { data: overview } = useQuery({ queryKey: ['portfolio-overview'], queryFn: fetchPortfolioOverview });
  const { data: activities } = useQuery({ queryKey: ['activities'], queryFn: fetchActivities });

  useEffect(() => {
    if (kpis) setKPIs(kpis);
  }, [kpis, setKPIs]);

  if (loadingKPIs || loadingMap) {
    return (
      <div className="flex items-center justify-center h-full text-green-600">
        <Loader2 className="animate-spin mr-2" /> Loading TNFD Portfolio...
      </div>
    );
  }

  const chartData = overview 
    ? Object.entries(activeToggle === 'impact' ? overview.impact_distribution : overview.dependency_distribution)
        .map(([name, value]) => ({ name, value }))
    : [];

  const donutData = overview
    ? Object.entries(activeToggle === 'impact' ? overview.overall_impact_counts : overview.overall_dep_counts)
        .map(([name, value]) => ({ name, value }))
    : [];


  return (
    <div className="space-y-6 pb-12 animate-in fade-in duration-700">
      <header className="flex justify-between items-start">
        <div className="flex flex-col">
          <h1 className="text-3xl font-black text-gray-800 tracking-tighter">
            Impact &amp; Dependency Dashboard
          </h1>
          <p className="text-xs font-black text-green-600 uppercase tracking-widest mt-1">
            Portfolio Overview
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-2xl font-black text-sm shadow-xl shadow-green-100 flex items-center gap-2 transition-all active:scale-95"
        >
          <UploadCloud size={18} /> New Site Analysis
        </button>
      </header>

      {/* KPI STRIP */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard icon={<Activity size={18} />} title="Analysed Sites" value={kpis?.analysed_sites} />
        <KPICard icon={<TrendingUp size={18} />} title="Top Pressure" value={kpis?.top_pressure} color="text-red-500" />
        <KPICard icon={<Layers size={18} />} title="Top Dependency" value={kpis?.top_dependency} color="text-red-500" />
        <KPICard icon={<ShieldCheck size={18} />} title="TNFD Priority" value={kpis?.tnfd_priority_sites} sub="Material Sites" color="text-orange-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart Section */}
        <div className="lg:col-span-2 bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm">
          <div className="flex justify-between items-center mb-8">
            <div className="space-y-1">
              <h3 className="text-base font-black text-gray-800 uppercase tracking-widest flex items-center gap-2">
                <BarChart3 size={16} className="text-green-600" /> Portfolio Distribution
              </h3>
              <p className="text-xs text-gray-400 font-medium tracking-tight">Combined Pressures & Dependency Risks across all assets.</p>
            </div>
            <div className="flex bg-gray-50 p-1 rounded-xl border border-gray-100">
              {['impact', 'dependency'].map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveToggle(t)}
                  className={cn(
                    "px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all",
                    activeToggle === t ? "bg-white text-gray-800 shadow-sm border border-gray-100" : "text-gray-400 hover:text-gray-600"
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 800, fill: '#9ca3af' }} dy={10} />
                <YAxis domain={[0, 5]} axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 800, fill: '#9ca3af' }} />
                <Tooltip cursor={{ fill: '#f9fafb' }} content={<CustomTooltip />} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={
                      entry.value <= 1.5 ? COLORS.VL :
                      entry.value <= 2.5 ? COLORS.L :
                      entry.value <= 3.5 ? COLORS.M :
                      entry.value <= 4.5 ? COLORS.H :
                      COLORS.VH
                    } />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Summary */}
        <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm flex flex-col items-center justify-between">
          <h3 className="text-base font-black text-gray-800 uppercase tracking-widest self-start flex items-center gap-2">
            <PieIcon size={16} className="text-green-600" /> Overall {activeToggle === 'impact' ? 'Impact' : 'Dependency'}
          </h3>
          <div className="relative w-full aspect-square flex items-center justify-center max-w-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={donutData} innerRadius={65} outerRadius={90} paddingAngle={8} dataKey="value" stroke="none">
                  {donutData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-black text-gray-800">{kpis?.analysed_sites}</span>
              <span className="text-[11px] font-black text-gray-400 uppercase tracking-widest">Sites Total</span>
            </div>
          </div>
          <div className="w-full grid grid-cols-2 gap-2 mt-4">
            {donutData.map(d => (
              <div key={d.name} className="flex items-center gap-2 p-2 rounded-xl bg-gray-50/50">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[d.name] }} />
                <span className="text-xs font-black text-gray-500 uppercase">{d.name}</span>
                <span className="ml-auto text-xs font-black text-gray-800">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map & List Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-[2rem] border border-gray-100 p-4 shadow-sm h-[450px] relative overflow-hidden">
          <div className="absolute top-6 left-6 z-10 bg-white/80 backdrop-blur-md px-4 py-2 rounded-full border border-gray-100 flex items-center gap-2 shadow-sm">
            <MapIcon size={14} className="text-green-600" />
            <span className="text-xs font-black uppercase tracking-widest text-gray-800">Portfolio Spatial Distribution</span>
          </div>
          <Map sites={mapData?.features?.map(f => ({ ...f.properties, geometry: f.geometry })) || []} />
        </div>

        <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm">
          <h3 className="text-base font-black text-gray-800 uppercase tracking-widest mb-6 flex items-center gap-2">
            <ListFilter size={16} className="text-green-600" /> Priority Sites
          </h3>
          <div className="space-y-4">
            {topSites?.map(s => (
              <div key={s.site_id} className="flex items-center gap-4 group cursor-pointer hover:bg-gray-50 p-3 rounded-[1.5rem] transition-all border border-transparent hover:border-gray-100">
                <div className={cn(
                  "w-12 h-12 rounded-2xl flex items-center justify-center font-black text-lg",
                  "bg-gray-50 text-gray-400 group-hover:scale-110 transition-transform",
                  s.impact_level === 'VH' ? "text-red-500 bg-red-50" : s.impact_level === 'H' ? "text-orange-500 bg-orange-50" : "text-green-600 bg-green-50"
                )}>
                  {Math.round(s.priority_score)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-black text-gray-800 text-sm truncate">{s.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-black text-gray-400 uppercase">{s.priority_tier}</span>
                    <div className="h-1 w-1 rounded-full bg-gray-200" />
                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">{s.impact_level} Impact</span>
                  </div>
                </div>
                <ChevronRight size={16} className="text-gray-300 group-hover:text-gray-800 transition-colors" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUpload && <UploadModal onClose={() => setShowUpload(false)} activities={activities} navigate={navigate} />}

      <footer className="pt-12 border-t border-gray-100 text-center opacity-40 hover:opacity-100 transition-opacity">
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
          Powered by ENCORE Nature Data • State of Nature v2.0 • CC BY-SA 4.0 Attribution Required
        </p>
      </footer>
    </div>
  );
}

function KPICard({ icon, title, value, sub, color = "text-gray-800" }) {
  return (
    <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-2 rounded-xl bg-gray-50 text-green-600">
          {icon}
        </div>
        <span className="text-[11px] font-black text-gray-400 uppercase tracking-widest">{title}</span>
      </div>
      <div className="flex items-end gap-2">
        <h4 className={cn("text-4xl font-black leading-none tracking-tighter", color)}>{value || 0}</h4>
        {sub && <span className="text-[10px] font-black text-gray-400 uppercase mb-1">{sub}</span>}
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    const getLevelText = (v) => {
      if (v <= 1.5) return 'Very Low';
      if (v <= 2.5) return 'Low';
      if (v <= 3.5) return 'Medium';
      if (v <= 4.5) return 'High';
      return 'Very High';
    };
    return (
      <div className="bg-white/90 backdrop-blur-md border border-gray-100 p-3 rounded-xl shadow-xl">
        <p className="text-xs font-black text-gray-800 uppercase mb-1">{payload[0].payload.name}</p>
        <p className="text-xl font-black text-green-600">{val.toFixed(2)} <span className="text-xs text-gray-400">/ 5.0</span></p>
        <p className="text-[10px] font-black text-gray-400 uppercase mt-1">Concern Level: {getLevelText(val)}</p>
      </div>
    );
  }
  return null;
}

function UploadModal({ onClose, activities, navigate }) {
  const [name, setName] = useState('');
  const [selected, setSelected] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!file || !name || selected.length === 0) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('site_name', name);
    formData.append('activities_json', JSON.stringify(selected));
    try {
      const result = await uploadKml(formData);
      onClose();
      if (result && result.site_id) {
        navigate(`/sites/${result.site_id}`);
      } else {
        window.location.reload();
      }
    } catch (e) {
      console.error(e);
      alert("Analysis failed. Please check the file format and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-md z-[100] flex items-center justify-center p-6 animate-in fade-in zoom-in duration-300">
      <div className="bg-white rounded-[2.5rem] p-10 max-w-lg w-full shadow-2xl relative overflow-hidden border border-gray-100">
        <div className="absolute top-0 left-0 w-full h-2 bg-green-500" />
        <h2 className="text-3xl font-black text-gray-800 tracking-tighter mb-8 flex items-center gap-3">
          <UploadCloud size={24} className="text-green-600" /> New Area Analysis
        </h2>

        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Asset Name</label>
            <input
              value={name} onChange={e => setName(e.target.value)}
              className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-green-100 transition-all font-bold text-gray-700"
              placeholder="e.g. Alpena Cement Plant"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Economic Activities (TNFD L2)</label>
            <select
              onChange={e => !selected.includes(e.target.value) && setSelected([...selected, e.target.value])}
              className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-green-100 transition-all font-bold text-gray-700 appearance-none"
            >
              <option value="">Select activities...</option>
              {activities?.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
            <div className="flex flex-wrap gap-2 mt-3">
              {selected.map(s => (
                <div key={s} className="bg-green-50 text-green-700 px-3 py-1 rounded-full text-[10px] font-black flex items-center gap-2">
                  {s} <button onClick={() => setSelected(selected.filter(x => x !== s))}>×</button>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Spatial File (KML/KMZ)</label>
            <div className={cn(
              "border-2 border-dashed border-gray-100 rounded-[2rem] p-8 text-center transition-all cursor-pointer hover:bg-gray-50",
              file && "border-green-200 bg-green-50/30"
            )}>
              <input type="file" onChange={e => setFile(e.target.files[0])} className="hidden" id="kml-up" />
              <label htmlFor="kml-up" className="cursor-pointer space-y-2">
                <div className="mx-auto w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-gray-400">
                  <UploadCloud size={20} />
                </div>
                <p className="text-xs font-bold text-gray-500">{file ? file.name : "Drag and drop or click to upload"}</p>
              </label>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mt-12">
          <button onClick={onClose} className="flex-1 py-4 font-black text-gray-400 hover:text-gray-800 transition-colors uppercase tracking-widest text-xs">Cancel</button>
          <button
            disabled={loading}
            onClick={handleSubmit}
            className="flex-[2] bg-green-600 hover:bg-green-700 text-white font-black py-4 rounded-[1.5rem] shadow-xl shadow-green-100 transition-all active:scale-95 flex items-center justify-center gap-2 text-sm uppercase tracking-widest"
          >
            {loading ? <Loader2 className="animate-spin" /> : "Initiate Analysis"}
          </button>
        </div>
      </div>
    </div>
  );
}

