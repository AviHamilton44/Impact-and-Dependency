import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchSiteDetail } from '../api';
import { 
  ArrowLeft, 
  MapPin, 
  Calendar, 
  AlertTriangle,
  Activity,
  ShieldCheck,
  ExternalLink,
  Loader2,
  TrendingUp,
  Sliders,
  Database,
  Map as MapIcon,
  Search,
  ChevronDown,
  ChevronUp,
  Layers,
  Info
} from 'lucide-react';
import { cn } from '../lib/utils';
import { MapContainer, TileLayer, GeoJSON, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';

// Fix leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const LEVEL_COLORS = {
  VL: 'text-yellow-600 bg-yellow-50 border-yellow-100',
  L: 'text-amber-600 bg-amber-50 border-amber-100',
  M: 'text-orange-600 bg-orange-50 border-orange-100',
  H: 'text-red-500 bg-red-50 border-red-100',
  VH: 'text-red-700 bg-red-100 border-red-200'
};

const DYNAMIC_COLORS = {
  VL: '#eab308',
  L: '#f59e0b',
  M: '#f97316',
  H: '#ef4444',
  VH: '#b91c1c'
};

export default function SiteDetail() {
  const { siteId } = useParams();
  const [activeTab, setActiveTab] = useState('summary');
  const [expandedCard, setExpandedCard] = useState({ type: null, index: null });
  const [thematicLayer, setThematicLayer] = useState('none');
  const [indicatorSearch, setIndicatorSearch] = useState('');
  const [indicatorFilter, setIndicatorFilter] = useState('all');

  const { data: detail, isLoading } = useQuery({ 
    queryKey: ['site-detail', siteId], 
    queryFn: () => fetchSiteDetail(siteId) 
  });

  if (isLoading) {
    return (
      <div className="p-20 text-center text-green-600 font-black animate-pulse flex flex-col items-center justify-center">
        <Loader2 className="animate-spin mb-4" size={40} /> 
        <span>Calculating Dynamic TNFD Scores & spatial indices...</span>
      </div>
    );
  }

  if (!detail || !detail.analysis) {
    return <div className="p-20 text-center font-black">Site data not found.</div>;
  }

  const { metadata, analysis } = detail;
  const center = metadata.latitude && metadata.longitude ? [metadata.latitude, metadata.longitude] : [20, 0];

  // Helper to toggle expand
  const toggleExpand = (type, index) => {
    if (expandedCard.type === type && expandedCard.index === index) {
      setExpandedCard({ type: null, index: null });
    } else {
      setExpandedCard({ type, index });
    }
  };

  // Prepare chart data for dependencies
  const radarDepData = analysis.all_dependencies?.map(d => ({
    subject: d.category,
    value: d.score,
    fullMark: 100
  })) || [];

  // Prepare chart data for impacts
  const radarImpData = analysis.all_impacts?.map(i => ({
    subject: i.category,
    value: i.score,
    fullMark: 100
  })) || [];

  // Map thematic layers to indicator values
  const getThematicLayerValue = () => {
    const indicators = analysis.all_indicators || {};
    switch (thematicLayer) {
      case 'protected_area': return indicators.protected_area_overlap || 50;
      case 'kba': return indicators.kba_overlap || 50;
      case 'forest_cover': return indicators.forest_cover || 50;
      case 'water_stress': return indicators.water_stress || 50;
      case 'species_richness': return indicators.species_richness || 50;
      case 'ndvi': return indicators.ndvi || 50;
      case 'habitat': return indicators.ecosystem_integrity || 50;
      default: return 0;
    }
  };

  const getThematicColor = (val) => {
    if (thematicLayer === 'water_stress') {
      return val > 75 ? '#b91c1c' : val > 50 ? '#ef4444' : val > 25 ? '#f97316' : '#3b82f6';
    }
    // Greenish for environmental/ecological value
    return val > 75 ? '#065f46' : val > 50 ? '#059669' : val > 25 ? '#10b981' : '#a7f3d0';
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-8 duration-700 pb-20">
      {/* HEADER */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-sm">
        <div className="flex items-center gap-6">
          <Link to="/sites" className="p-4 bg-white border border-gray-100 rounded-2xl shadow-sm hover:bg-gray-50 transition-all text-gray-400 hover:text-gray-800">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-1">
              <h1 className="text-3xl font-black text-gray-800 tracking-tighter">{metadata.name}</h1>
              {analysis.is_tnfd_priority && (
                <div className="px-3 py-1 bg-red-50 text-red-600 border border-red-100 rounded-full text-xs font-black uppercase tracking-widest flex items-center gap-1.5 shadow-sm shadow-red-50">
                  <AlertTriangle size={12} /> TNFD Priority Site
                </div>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs font-black text-gray-400 uppercase tracking-widest">
              <div className="flex items-center gap-1"><MapPin size={12}/> {metadata.country}</div>
              <div className="h-1 w-1 rounded-full bg-gray-200" />
              <div className="flex items-center gap-1"><Calendar size={12}/> {new Date(metadata.created_at).toLocaleDateString()}</div>
              <div className="h-1 w-1 rounded-full bg-gray-200" />
              <div className="flex items-center gap-1"><Activity size={12}/> Archetype: {analysis.archetype?.toUpperCase()}</div>
            </div>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {metadata.activities?.map(act => (
            <span key={act} className="px-3 py-1.5 bg-green-50 text-green-700 border border-green-100 rounded-xl text-[10px] font-black uppercase tracking-wider">
              {act}
            </span>
          ))}
        </div>
      </header>

      {/* KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard 
          title="Overall Dependency Index" 
          value={analysis.dependency_risk_score} 
          sub={analysis.dependency_risk_level} 
          subClass={LEVEL_COLORS[analysis.dependency_risk_level]}
          colorClass="text-emerald-600"
        />
        <KPICard 
          title="Overall Impact Index" 
          value={analysis.impact_score} 
          sub={analysis.impact_level} 
          subClass={LEVEL_COLORS[analysis.impact_level]}
          colorClass="text-rose-600"
        />
        <KPICard 
          title="TNFD Priority Level" 
          value={analysis.priority_score} 
          sub={analysis.priority_tier} 
          subClass="text-orange-700 bg-orange-50 border-orange-100"
          colorClass="text-orange-600"
        />
        <KPICard 
          title="Spatial Data Confidence" 
          value={`${analysis.data_quality?.confidence_pct?.toFixed(0)}%`} 
          sub={analysis.data_quality?.confidence?.toUpperCase()} 
          subClass={analysis.data_quality?.confidence === 'high' ? 'text-green-700 bg-green-50 border-green-100' : 'text-amber-700 bg-amber-50 border-amber-100'}
          colorClass="text-blue-600"
        />
      </div>

      {/* TABS */}
      <div className="border-b border-gray-100 flex gap-8">
        {[
          { id: 'summary', label: 'Summary' },
          { id: 'dependencies', label: 'Dependencies' },
          { id: 'impacts', label: 'Impacts' },
          { id: 'map', label: 'Thematic Maps & Spatial' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "pb-4 text-xs font-black uppercase tracking-[0.2em] transition-all relative",
              activeTab === tab.id ? "text-gray-800" : "text-gray-300 hover:text-gray-500"
            )}
          >
            {tab.label}
            {activeTab === tab.id && <div className="absolute bottom-0 left-0 w-full h-1 bg-green-600 rounded-full" />}
          </button>
        ))}
      </div>

      {/* SUMMARY TAB */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top 5 Dependencies */}
          <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-6">
            <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest flex items-center gap-2">
              <Database size={16} className="text-emerald-600" /> Top 5 Material Dependencies
            </h3>
            <div className="space-y-4">
              {analysis.top_dependencies?.map((dep, index) => (
                <div key={index} className="border border-gray-100 rounded-2xl p-6 space-y-4 hover:border-emerald-100 transition-all">
                  <div className="flex items-center justify-between cursor-pointer" onClick={() => toggleExpand('dep', index)}>
                    <div className="space-y-1">
                      <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{dep.sensitivity_index_name}</p>
                      <h4 className="text-sm font-black text-gray-800 uppercase tracking-tighter">{dep.category}</h4>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className="text-[10px] font-bold text-gray-400 block leading-none">SCORE</span>
                        <span className="text-lg font-black text-emerald-600">{dep.score}</span>
                      </div>
                      <span className={cn("px-2.5 py-1 rounded-full text-[10px] font-black uppercase border", LEVEL_COLORS[dep.level])}>
                        {dep.level}
                      </span>
                      {expandedCard.type === 'dep' && expandedCard.index === index ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>
                  </div>

                  {expandedCard.type === 'dep' && expandedCard.index === index && (
                    <div className="pt-4 border-t border-gray-50 space-y-4 text-xs text-gray-600 animate-in fade-in duration-300">
                      <p className="leading-relaxed font-medium italic">"{dep.description}"</p>
                      <div className="grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded-xl text-center">
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">ENCORE Weight</span>
                          <span className="font-bold text-gray-700">{dep.encore_weight} ({dep.encore_rating})</span>
                        </div>
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">Sensitivity Score</span>
                          <span className="font-bold text-gray-700">{dep.sensitivity_score}</span>
                        </div>
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">Confidence</span>
                          <span className="font-bold text-gray-700">{analysis.data_quality?.confidence_pct?.toFixed(0)}%</span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <span className="text-[9px] font-black text-gray-400 block uppercase">Calculated Environmental Indicators</span>
                        <div className="grid grid-cols-2 gap-2">
                          {dep.indicators?.map((ind, i) => (
                            <div key={i} className="flex justify-between bg-white border border-gray-100 p-2 rounded-lg">
                              <span className="font-bold text-[10px] text-gray-500 truncate" title={ind.name}>{ind.name}</span>
                              <span className="font-black text-[10px] text-gray-800 ml-2">{ind.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="text-[10px] text-gray-400 font-bold flex items-center gap-1">
                        <Info size={10} /> Sources: {dep.dataset_sources?.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Top 5 Impacts */}
          <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-6">
            <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest flex items-center gap-2">
              <TrendingUp size={16} className="text-rose-600" /> Top 5 Material Impacts
            </h3>
            <div className="space-y-4">
              {analysis.top_impacts?.map((imp, index) => (
                <div key={index} className="border border-gray-100 rounded-2xl p-6 space-y-4 hover:border-rose-100 transition-all">
                  <div className="flex items-center justify-between cursor-pointer" onClick={() => toggleExpand('imp', index)}>
                    <div className="space-y-1">
                      <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{imp.sensitivity_index_name}</p>
                      <h4 className="text-sm font-black text-gray-800 uppercase tracking-tighter">{imp.category}</h4>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className="text-[10px] font-bold text-gray-400 block leading-none">SCORE</span>
                        <span className="text-lg font-black text-rose-600">{imp.score}</span>
                      </div>
                      <span className={cn("px-2.5 py-1 rounded-full text-[10px] font-black uppercase border", LEVEL_COLORS[imp.level])}>
                        {imp.level}
                      </span>
                      {expandedCard.type === 'imp' && expandedCard.index === index ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>
                  </div>

                  {expandedCard.type === 'imp' && expandedCard.index === index && (
                    <div className="pt-4 border-t border-gray-50 space-y-4 text-xs text-gray-600 animate-in fade-in duration-300">
                      <p className="leading-relaxed font-medium italic">"{imp.description}"</p>
                      <div className="grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded-xl text-center">
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">ENCORE Weight</span>
                          <span className="font-bold text-gray-700">{imp.encore_weight} ({imp.encore_rating})</span>
                        </div>
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">Sensitivity Score</span>
                          <span className="font-bold text-gray-700">{imp.sensitivity_score}</span>
                        </div>
                        <div>
                          <span className="text-[9px] font-black text-gray-400 block uppercase mb-1">Confidence</span>
                          <span className="font-bold text-gray-700">{analysis.data_quality?.confidence_pct?.toFixed(0)}%</span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <span className="text-[9px] font-black text-gray-400 block uppercase">Calculated Environmental Indicators</span>
                        <div className="grid grid-cols-2 gap-2">
                          {imp.indicators?.map((ind, i) => (
                            <div key={i} className="flex justify-between bg-white border border-gray-100 p-2 rounded-lg">
                              <span className="font-bold text-[10px] text-gray-500 truncate" title={ind.name}>{ind.name}</span>
                              <span className="font-black text-[10px] text-gray-800 ml-2">{ind.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="text-[10px] text-gray-400 font-bold flex items-center gap-1">
                        <Info size={10} /> Sources: {imp.dataset_sources?.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* DEPENDENCIES TAB */}
      {activeTab === 'dependencies' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Charts Panel */}
            <div className="lg:col-span-2 bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-6">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest">Dependency Risk Profiler</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Radar Chart */}
                <div className="h-[260px] flex flex-col items-center justify-center">
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Dependency Profile (Radar)</span>
                  <ResponsiveContainer width="100%" height="90%">
                    <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarDepData}>
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fontWeight: 700, fill: '#6b7280' }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 8 }} />
                      <Radar name="Dependency" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                {/* Bar Chart */}
                <div className="h-[260px] flex flex-col items-center justify-center">
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Risk Comparison (Bar)</span>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={analysis.all_dependencies} layout="vertical" margin={{ left: 10, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
                      <XAxis type="number" domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 8 }} />
                      <YAxis dataKey="category" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 8, fontWeight: 700 }} width={80} />
                      <Tooltip cursor={{ fill: '#f9fafb' }} />
                      <Bar dataKey="score" fill="#10b981" radius={[0, 4, 4, 0]} barSize={12} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Gauges Panel */}
            <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-4 flex flex-col justify-between">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest">Environmental Sensitivities</h3>
              <div className="grid grid-cols-2 gap-4">
                <GaugeChart value={analysis.sensitivity_indices?.WaterSensitivity} title="Water" colorClass="#3b82f6" />
                <GaugeChart value={analysis.sensitivity_indices?.HabitatSensitivity} title="Habitat" colorClass="#10b981" />
                <GaugeChart value={analysis.sensitivity_indices?.ClimateSensitivity} title="Climate" colorClass="#f59e0b" />
                <GaugeChart value={analysis.sensitivity_indices?.SoilSensitivity} title="Soil" colorClass="#8b5cf6" />
              </div>
            </div>
          </div>

          {/* Full Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analysis.all_dependencies?.map((dep, index) => (
              <div key={index} className="bg-white border border-gray-100 rounded-3xl p-8 shadow-sm flex flex-col justify-between hover:shadow-md hover:border-emerald-100 transition-all">
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest">{dep.sensitivity_index_name}</span>
                    <span className={cn("px-2 py-0.5 rounded-full text-[9px] font-black uppercase border", LEVEL_COLORS[dep.level])}>
                      {dep.level}
                    </span>
                  </div>
                  <h4 className="text-base font-black text-gray-800 uppercase tracking-tight">{dep.category}</h4>
                  <p className="text-xs text-gray-400 leading-relaxed italic">"{dep.description}"</p>
                </div>

                <div className="mt-8 pt-6 border-t border-gray-50 flex items-center justify-between">
                  <div className="text-left">
                    <span className="text-[9px] font-black text-gray-400 uppercase block mb-1">ENCORE Rating</span>
                    <span className="font-bold text-xs text-gray-700">{dep.encore_rating}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-black text-gray-400 uppercase block mb-1">Dynamic Score</span>
                    <span className="font-black text-lg text-emerald-600">{dep.score}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* IMPACTS TAB */}
      {activeTab === 'impacts' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Charts Panel */}
            <div className="lg:col-span-2 bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-6">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest">Impact Footprint Profiler</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Radar Chart */}
                <div className="h-[260px] flex flex-col items-center justify-center">
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Impact Profile (Radar)</span>
                  <ResponsiveContainer width="100%" height="90%">
                    <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarImpData}>
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fontWeight: 700, fill: '#6b7280' }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 8 }} />
                      <Radar name="Impact" dataKey="value" stroke="#ef4444" fill="#ef4444" fillOpacity={0.4} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                {/* Bar Chart */}
                <div className="h-[260px] flex flex-col items-center justify-center">
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Risk Comparison (Bar)</span>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={analysis.all_impacts} layout="vertical" margin={{ left: 10, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
                      <XAxis type="number" domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 8 }} />
                      <YAxis dataKey="category" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 8, fontWeight: 700 }} width={80} />
                      <Tooltip cursor={{ fill: '#f9fafb' }} />
                      <Bar dataKey="score" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={12} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Gauges Panel */}
            <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-4 flex flex-col justify-between">
              <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest">Environmental Sensitivities</h3>
              <div className="grid grid-cols-2 gap-4">
                <GaugeChart value={analysis.sensitivity_indices?.WaterSensitivity} title="Water" colorClass="#3b82f6" />
                <GaugeChart value={analysis.sensitivity_indices?.HabitatSensitivity} title="Habitat" colorClass="#10b981" />
                <GaugeChart value={analysis.sensitivity_indices?.ClimateSensitivity} title="Climate" colorClass="#f59e0b" />
                <GaugeChart value={analysis.sensitivity_indices?.SoilSensitivity} title="Soil" colorClass="#8b5cf6" />
              </div>
            </div>
          </div>

          {/* Full Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analysis.all_impacts?.map((imp, index) => (
              <div key={index} className="bg-white border border-gray-100 rounded-3xl p-8 shadow-sm flex flex-col justify-between hover:shadow-md hover:border-rose-100 transition-all">
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest">{imp.sensitivity_index_name}</span>
                    <span className={cn("px-2 py-0.5 rounded-full text-[9px] font-black uppercase border", LEVEL_COLORS[imp.level])}>
                      {imp.level}
                    </span>
                  </div>
                  <h4 className="text-base font-black text-gray-800 uppercase tracking-tight">{imp.category}</h4>
                  <p className="text-xs text-gray-400 leading-relaxed italic">"{imp.description}"</p>
                </div>

                <div className="mt-8 pt-6 border-t border-gray-50 flex items-center justify-between">
                  <div className="text-left">
                    <span className="text-[9px] font-black text-gray-400 uppercase block mb-1">ENCORE Rating</span>
                    <span className="font-bold text-xs text-gray-700">{imp.encore_rating}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-black text-gray-400 uppercase block mb-1">Dynamic Score</span>
                    <span className="font-black text-lg text-rose-600">{imp.score}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MAP & SPATIAL TAB */}
      {activeTab === 'map' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Map Frame */}
            <div className="lg:col-span-3 bg-white border border-gray-100 rounded-[2rem] p-4 shadow-sm h-[500px] relative overflow-hidden">
              <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '1.5rem' }}>
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                
                {metadata.geometry && (
                  <GeoJSON 
                    data={metadata.geometry} 
                    style={{
                      color: getThematicColor(getThematicLayerValue()),
                      weight: 3,
                      fillOpacity: 0.35,
                      fillColor: getThematicColor(getThematicLayerValue())
                    }}
                  />
                )}

                {/* Thematic circle layer overlay representing indicator intensity */}
                {thematicLayer !== 'none' && (
                  <Circle 
                    center={center} 
                    radius={3000} 
                    pathOptions={{
                      color: getThematicColor(getThematicLayerValue()),
                      fillColor: getThematicColor(getThematicLayerValue()),
                      fillOpacity: 0.45,
                      dashArray: thematicLayer === 'protected_area' || thematicLayer === 'kba' ? '5, 5' : '0'
                    }}
                  >
                    <Popup>
                      <div className="p-2 space-y-1 text-xs">
                        <span className="font-black uppercase tracking-widest text-[9px] text-gray-400 block">Thematic Layer</span>
                        <h4 className="font-black text-gray-800 uppercase">{thematicLayer.replace("_", " ")}</h4>
                        <div className="flex justify-between items-center border-t pt-1.5 mt-1">
                          <span className="font-bold text-gray-500">Site Score:</span>
                          <span className="font-black text-emerald-600">{getThematicLayerValue()}/100</span>
                        </div>
                      </div>
                    </Popup>
                  </Circle>
                )}
              </MapContainer>
            </div>

            {/* Map Layers Toggles Panel */}
            <div className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest flex items-center gap-2">
                  <Layers size={16} className="text-green-600" /> GIS Thematic Overlays
                </h3>
                <p className="text-xs text-gray-400 leading-relaxed font-medium">Select a layer to project dynamic spatial indicators onto the map.</p>

                <div className="space-y-2">
                  {[
                    { id: 'none', label: 'Default View (No Overlay)' },
                    { id: 'protected_area', label: 'Protected Areas (WDPA)' },
                    { id: 'kba', label: 'Key Biodiversity Areas (KBA)' },
                    { id: 'forest_cover', label: 'Forest Cover (Hansen)' },
                    { id: 'water_stress', label: 'Water Stress (Aqueduct)' },
                    { id: 'species_richness', label: 'Species Richness (IUCN)' },
                    { id: 'ndvi', label: 'NDVI Greenness (MODIS)' },
                    { id: 'habitat', label: 'Habitat Integrity' }
                  ].map(layer => (
                    <label key={layer.id} className={cn(
                      "flex items-center gap-3 p-3 rounded-xl border border-gray-50 hover:bg-gray-50 cursor-pointer transition-all",
                      thematicLayer === layer.id && "bg-green-50/50 border-green-100 font-bold"
                    )}>
                      <input 
                        type="radio" 
                        name="theme" 
                        value={layer.id} 
                        checked={thematicLayer === layer.id}
                        onChange={() => setThematicLayer(layer.id)}
                        className="accent-green-600"
                      />
                      <span className="text-xs text-gray-700">{layer.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {thematicLayer !== 'none' && (
                <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100 space-y-2 animate-in fade-in duration-300">
                  <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest block">Legend / Value Scale</span>
                  <div className="flex justify-between items-center text-[10px] font-black text-gray-700">
                    <span>Low Concern</span>
                    <span>High Concern</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-gradient-to-r from-emerald-200 to-rose-600" />
                </div>
              )}
            </div>
          </div>

          {/* Full List of 36 Spatial Indicators */}
          <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest">36 Dynamic Spatial Indicators</h3>
                <p className="text-xs text-gray-400 font-medium">Full raw database values extracted from remote sensing grids.</p>
              </div>
              
              <div className="flex gap-2">
                {/* Theme filter buttons */}
                {['all', 'water', 'habitat', 'climate', 'soil'].map(theme => (
                  <button
                    key={theme}
                    onClick={() => setIndicatorFilter(theme)}
                    className={cn(
                      "px-3.5 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all border border-gray-100",
                      indicatorFilter === theme ? "bg-green-600 text-white border-green-600" : "bg-white text-gray-500 hover:bg-gray-50"
                    )}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            {/* Grid of indicators */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(analysis.all_indicators || {}).map(([key, val]) => {
                const key_name = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
                
                // Grouping logic for indicators
                let group = 'other';
                if (['water_stress', 'groundwater_availability', 'surface_water_availability', 'distance_to_rivers', 'flood_risk', 'drought_risk', 'water_bodies'].includes(key)) {
                  group = 'water';
                } else if (['forest_cover', 'protected_area_overlap', 'kba_overlap', 'species_richness', 'threatened_species', 'endemic_species', 'mammal_richness', 'bird_richness', 'edna_richness', 'habitat_fragmentation', 'connectivity', 'wetland_area', 'grassland', 'mangrove_area'].includes(key)) {
                  group = 'habitat';
                } else if (['carbon_stock', 'above_ground_biomass', 'ndvi', 'evi', 'temperature', 'rainfall', 'fire_risk', 'forest_loss'].includes(key)) {
                  group = 'climate';
                } else if (['soil_organic_carbon', 'soil_moisture', 'soil_fertility', 'soil_erosion', 'agricultural_land', 'built_up_area', 'ecosystem_integrity'].includes(key)) {
                  group = 'soil';
                }

                if (indicatorFilter !== 'all' && indicatorFilter !== group) return null;

                return (
                  <div key={key} className="bg-gray-50/50 border border-gray-100 rounded-2xl p-4 flex justify-between items-center">
                    <div>
                      <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest block mb-0.5">{group}</span>
                      <h4 className="text-xs font-bold text-gray-700 capitalize">{key.replace(/_/g, ' ')}</h4>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-black text-gray-800">{val}</span>
                      <div className="h-6 w-1 rounded-full" style={{ backgroundColor: val > 75 ? DYNAMIC_COLORS.VH : val > 50 ? DYNAMIC_COLORS.H : val > 25 ? DYNAMIC_COLORS.M : DYNAMIC_COLORS.L }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="pt-20 opacity-40">
        <div className="bg-gray-50 p-8 rounded-[2.5rem] border border-gray-100 flex flex-col items-center gap-4">
          <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest text-center max-w-2xl leading-relaxed">
            MANDATORY ATTRIBUTION: This dashboard utilizes metadata from the ENCORE tool (Natural Capital Finance Alliance). 
            Licensed under CC BY-SA 4.0. DOI: 10.34892/vcmx-6308. Data derived from LEAP v2.7 Framework alignment.
          </p>
          <div className="flex gap-4">
            <ExternalLink size={14} className="text-gray-300" />
            <div className="h-4 w-[1px] bg-gray-200" />
            <span className="text-[10px] font-black text-gray-800 uppercase tracking-widest underline cursor-pointer">View ENCORE Source</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function KPICard({ title, value, sub, subClass, colorClass }) {
  return (
    <div className="bg-white rounded-[2rem] border border-gray-100 p-6 flex flex-col items-center text-center shadow-sm">
      <span className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2">{title}</span>
      <h4 className={cn("text-3xl font-black tracking-tighter mb-2 leading-none", colorClass)}>{value}</h4>
      <span className={cn("px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase border", subClass)}>
        {sub}
      </span>
    </div>
  );
}

function GaugeChart({ value, title, colorClass }) {
  const data = [
    { value: value || 0 },
    { value: 100 - (value || 0) }
  ];
  return (
    <div className="bg-gray-50 rounded-2xl border border-gray-100 p-4 flex flex-col items-center justify-center text-center shadow-sm">
      <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">{title}</span>
      <div className="relative w-28 h-14 overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="100%"
              startAngle={180}
              endAngle={0}
              innerRadius={30}
              outerRadius={40}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={colorClass} />
              <Cell fill="#e5e7eb" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute bottom-0 left-0 right-0 text-center">
          <span className="text-lg font-black text-gray-800">{Math.round(value || 0)}</span>
          <span className="text-[8px] text-gray-400 font-bold">/100</span>
        </div>
      </div>
    </div>
  );
}

// Inline PieChart components since they are simple Recharts imports
import { PieChart, Pie, Cell } from 'recharts';
