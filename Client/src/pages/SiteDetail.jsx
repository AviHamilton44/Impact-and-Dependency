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
  TrendingUp
} from 'lucide-react';
import { cn } from '../lib/utils';

export default function SiteDetail() {
  const { siteId } = useParams();
  const [activeTab, setActiveTab] = useState('impacts');
  
  const { data: detail, isLoading } = useQuery({ 
    queryKey: ['site-detail', siteId], 
    queryFn: () => fetchSiteDetail(siteId) 
  });

  if (isLoading) return <div className="p-20 text-center text-green-600 font-black animate-pulse"><Loader2 className="animate-spin mx-auto mb-4" /> Analyzing Site Data...</div>;
  if (!detail) return <div className="p-20 text-center font-black">Site not found.</div>;

  const { metadata, analysis } = detail;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-700 pb-20">
      <header className="flex items-center gap-6">
        <Link to="/sites" className="p-4 bg-white border border-gray-100 rounded-2xl shadow-sm hover:bg-gray-50 transition-all text-gray-400 hover:text-gray-800">
           <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
           <div className="flex items-center gap-3 mb-1">
             <h1 className="text-4xl font-black text-gray-800 tracking-tighter">{metadata.name}</h1>
             {analysis.is_tnfd_priority && (
                 <div className="px-3 py-1 bg-red-50 text-red-600 border border-red-100 rounded-full text-xs font-black uppercase tracking-widest flex items-center gap-1.5 shadow-sm shadow-red-50">
                   <AlertTriangle size={12} /> TNFD Priority
                 </div>
             )}
           </div>
           <div className="flex items-center gap-4">
             <div className="flex items-center gap-1 text-xs font-black text-gray-400 uppercase tracking-widest"><MapPin size={12}/> {metadata.country}</div>
             <div className="h-1 w-1 rounded-full bg-gray-200" />
             <div className="flex items-center gap-1 text-xs font-black text-gray-400 uppercase tracking-widest"><Calendar size={12}/> {new Date(metadata.created_at).toLocaleDateString()}</div>
             <div className="h-1 w-1 rounded-full bg-gray-200" />
             <div className="flex items-center gap-1 text-xs font-black text-gray-400 uppercase tracking-widest"><Activity size={12}/> Biome: {metadata.biome_code}</div>
           </div>
        </div>
      </header>

      {/* KPI STRIP */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <DetailKPICard title="Priority Score" value={Math.round(analysis.priority_score)} sub={analysis.priority_tier} color="text-green-600" />
         <DetailKPICard title="Impact Level" value={analysis.impact_level} sub="Normalized IS" color="text-red-500" />
         <DetailKPICard title="Dependency Risk" value={analysis.dependency_risk_level} sub="Max Risk Level" color="text-orange-500" />
      </div>


      {/* TABS */}
      <div className="border-b border-gray-100 flex gap-8">
        {['impacts', 'dependencies'].map(t => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={cn(
              "pb-4 text-xs font-black uppercase tracking-[0.2em] transition-all relative",
              activeTab === t ? "text-gray-800" : "text-gray-300 hover:text-gray-500"
            )}
          >
            {t}
            {activeTab === t && <div className="absolute bottom-0 left-0 w-full h-1 bg-green-600 rounded-full" />}
          </button>
        ))}
      </div>

      {activeTab === 'impacts' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in slide-in-from-left-4 duration-500">
           <div className="lg:col-span-2 space-y-8">
              <section className="bg-white rounded-[2.5rem] border border-gray-100 p-10 shadow-sm">
                 <h3 className="text-sm font-black text-gray-800 uppercase tracking-widest mb-8">TNFD Impact Architecture (v2.0)</h3>
                 <div className="space-y-4">
                    <ImpactRow label="Loss of Ecosystem Extent" dim="Dimension 1" data={analysis.impact_breakdown?.extent} />
                    <ImpactRow label="Freshwater Condition" dim="Dimension 2" data={analysis.impact_breakdown?.freshwater} />
                    <ImpactRow label="Terrestrial Condition" dim="Dimension 2" data={analysis.impact_breakdown?.terrestrial} />
                    <ImpactRow label="Species Population Decline" dim="Dimension 3" data={analysis.impact_breakdown?.population} />
                    <ImpactRow label="Extinction Risk Escalation" dim="Dimension 4" data={analysis.impact_breakdown?.extinction} />
                 </div>
              </section>

              <section className="bg-green-600 rounded-[2.5rem] p-10 text-white shadow-xl shadow-green-100 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-8 opacity-10"><TrendingUp size={120} /></div>
                 <h3 className="text-sm font-black uppercase tracking-widest mb-4 opacity-70">A3 Risk Pathway Analysis</h3>
                 <div className="space-y-6 relative z-10">
                    <p className="text-lg font-medium leading-relaxed opacity-90">
                      Based on the <strong>{analysis.impact_level}</strong> impact level identified at {metadata.name}, 
                      there is a projected transition risk to local biodiversity targets. 
                      Regulatory oversight is <strong>{analysis.is_tnfd_priority ? 'Highly likely' : 'Moderate'}</strong> for this asset.
                    </p>
                    <div className="flex gap-4">
                       <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all">Download Pathway</button>
                    </div>
                 </div>
              </section>
           </div>

           <div className="space-y-6">
              <DataQualityCard quality={analysis.data_quality} />
              <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm">
                 <h3 className="text-xs font-black text-gray-800 uppercase tracking-widest mb-6">Pressure Drivers</h3>
                 <div className="space-y-4">
                    <PressureDriver title="Land Use" level="VH" />
                    <PressureDriver title="Water Use" level="M" />
                    <PressureDriver title="Pollutants" level="L" />
                    <PressureDriver title="GHG" level="H" />
                 </div>
              </div>
           </div>
        </div>
      ) : (
        <div className="animate-in fade-in slide-in-from-right-4 duration-500">
           <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {/* This is a placeholder for the 25-card grid */}
              {[...Array(25)].map((_, i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-help group">
                   <div className="h-2 w-full bg-gray-50 rounded-full mb-4 overflow-hidden">
                      <div className="h-full bg-green-500 transition-all group-hover:scale-x-110 origin-left" style={{ width: `${((i * 17) % 70) + 30}%` }} />
                   </div>
                   <p className="text-[10px] font-black text-gray-400 uppercase tracking-tighter truncate">ES Service {i+1}</p>
                   <p className="text-xs font-black text-gray-800 mt-1 uppercase tracking-widest">{['VL', 'L', 'M', 'H', 'VH'][(i * 7) % 5]}</p>
                </div>
              ))}
           </div>
        </div>
      )}

      <footer className="pt-20 opacity-40">
        <div className="bg-gray-50 p-8 rounded-[2rem] border border-gray-100 flex flex-col items-center gap-4">
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

function DetailKPICard({ title, value, sub, color }) {
  return (
    <div className="bg-white rounded-[2rem] border border-gray-100 p-8 shadow-sm flex flex-col items-center text-center">
       <span className="text-xs font-black text-gray-400 uppercase tracking-[0.2em] mb-2">{title}</span>
       <h4 className={cn("text-5xl font-black tracking-tighter mb-1", color)}>{value}</h4>
       <span className="text-xs font-black text-gray-800 uppercase tracking-widest">{sub}</span>
    </div>
  );
}

function ImpactRow({ label, dim, data }) {
  const COLORS = { VL: '#fde047', L: '#fcd34d', M: '#fb923c', H: '#f87171', VH: '#dc2626' };
  return (
    <div className="grid grid-cols-4 items-center py-4 border-b border-gray-50 last:border-0 hover:bg-gray-50/50 transition-colors px-4 rounded-xl group">
       <div className="col-span-1">
          <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">{dim}</p>
          <p className="text-xs font-black text-gray-800 uppercase tracking-tighter">{label}</p>
       </div>
       <div className="col-span-1 flex justify-center">
          <div className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest border border-gray-100 bg-gray-50 text-gray-500">EP: {data?.ep || 'VL'}</div>
       </div>
       <div className="col-span-1 flex justify-center">
          <div className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest border border-gray-100 bg-gray-50 text-gray-500">SoN: {data?.son || 'VL'}</div>
       </div>
       <div className="col-span-1 flex justify-end items-center gap-3">
          <div className="text-right">
             <p className="text-[9px] font-black text-gray-300 uppercase leading-none">IMPACT</p>
             <p className="text-base font-black text-gray-800 leading-none mt-0.5">{data?.level || 'VL'}</p>
          </div>
          <div className="w-2.5 h-10 rounded-full group-hover:scale-x-150 transition-transform" style={{ backgroundColor: COLORS[data?.level] || '#eee' }} />
       </div>
    </div>
  );
}

function PressureDriver({ title, level }) {
   return (
     <div className="flex justify-between items-center group">
        <span className="text-xs font-bold text-gray-500">{title}</span>
        <div className="flex items-center gap-3">
           <div className="h-1.5 w-12 bg-gray-50 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full transition-all group-hover:w-full",
                  level === 'VH' || level === 'H' ? 'bg-red-500' : 'bg-green-500'
                )} 
                style={{ width: level === 'VH' ? '100%' : level === 'H' ? '80%' : level === 'M' ? '60%' : '30%' }} 
              />
           </div>
           <span className="text-xs font-black text-gray-800 w-4">{level}</span>
        </div>
     </div>
   );
}

function DataQualityCard({ quality }) {
   return (
      <div className={cn(
        "bg-white rounded-[2rem] border p-8 shadow-sm",
        quality?.confidence === 'low' ? "border-red-100" : "border-gray-100"
      )}>
         <h3 className="text-xs font-black text-gray-800 uppercase tracking-widest mb-4 flex items-center gap-2">
            <ShieldCheck size={16} className={quality?.confidence === 'low' ? "text-red-500" : "text-green-600"} /> Data Quality
         </h3>
         <div className="space-y-4">
            <div className="flex justify-between items-center">
               <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Confidence</span>
               <span className={cn(
                 "px-2 py-0.5 rounded text-[10px] font-black uppercase",
                 quality?.confidence === 'low' ? "bg-red-50 text-red-500" : "bg-green-50 text-green-600"
               )}>{quality?.confidence || 'High'}</span>
            </div>
            <div className="flex justify-between items-center">
               <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">SoN Measures</span>
               <span className="text-xs font-black text-gray-800 flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500" /> {quality?.measured_metrics || 0} Measured
               </span>
            </div>
         </div>
      </div>
   );
}

