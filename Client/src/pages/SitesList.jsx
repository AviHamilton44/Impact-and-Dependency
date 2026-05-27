import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchSites, clearSites, deleteSite } from '../api';
import { 
  Search, 
  MapPin, 
  Filter, 
  ChevronRight, 
  ArrowUpDown, 
  Download,
  AlertTriangle,
  Trash2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../lib/utils';

export default function SitesList() {
  const [searchTerm, setSearchTerm] = useState('');
  const { data: sites, isLoading, refetch } = useQuery({ queryKey: ['sites'], queryFn: fetchSites });

  const filteredSites = sites?.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.activities?.some(a => a.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleClearAll = async () => {
    if (window.confirm("Are you sure you want to remove all pre-existing sites? This cannot be undone.")) {
      try {
        await clearSites();
        refetch();
      } catch (err) {
        console.error(err);
        alert("Failed to clear sites.");
      }
    }
  };

  const handleDeleteSite = async (siteId) => {
    if (window.confirm("Are you sure you want to delete this site?")) {
      try {
        await deleteSite(siteId);
        refetch();
      } catch (err) {
        console.error(err);
        alert("Failed to delete site.");
      }
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div className="space-y-1">
          <p className="text-[10px] font-black text-green-800/40 uppercase tracking-[0.2em]">Inventory Management</p>
          <h1 className="text-3xl font-black text-gray-800 tracking-tighter">Portfolio Assets</h1>
        </div>
        <div className="flex gap-2 items-center">
          {sites && sites.length > 0 && (
            <button 
              onClick={handleClearAll}
              className="bg-red-50 hover:bg-red-100 text-red-600 border border-red-100 px-4 py-2.5 rounded-xl font-black text-xs uppercase tracking-wider flex items-center gap-2 transition-all active:scale-95 shadow-sm mr-2"
            >
              <Trash2 size={14} /> Clear All Assets
            </button>
          )}
          <button className="p-3 bg-white border border-gray-100 rounded-xl shadow-sm text-gray-400 hover:text-gray-800 transition-all"><Download size={18}/></button>
          <button className="p-3 bg-white border border-gray-100 rounded-xl shadow-sm text-gray-400 hover:text-gray-800 transition-all"><Filter size={18}/></button>
        </div>
      </header>

      {/* SEARCH STRIP */}
      <div className="bg-white p-2 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-2">
        <div className="flex-1 flex items-center gap-3 px-4 py-2">
          <Search size={18} className="text-gray-300" />
          <input 
            type="text" 
            placeholder="Search by site name, activity, or country..." 
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-transparent outline-none text-sm font-bold text-gray-700 placeholder:text-gray-300"
          />
        </div>
      </div>

      {/* TABLE */}
      <div className="bg-white border border-gray-100 rounded-[2.5rem] shadow-sm overflow-hidden flex flex-col min-h-[600px]">
        <div className="overflow-x-auto flex-1">
          <table className="w-full border-collapse">
            <thead className="bg-gray-50/50 border-b border-gray-100">
               <tr className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  <th className="px-8 py-5 text-left">Asset</th>
                  <th className="px-6 py-5 text-left">Primary Activity</th>
                  <th className="px-6 py-5 text-center">TNFD Status</th>
                  <th className="px-6 py-5 text-center flex items-center justify-center gap-1">Priority <ArrowUpDown size={10}/></th>
                  <th className="px-6 py-5 text-center">Pressures</th>
                  <th className="px-6 py-5 text-center">Dependencies</th>
                  <th className="px-6 py-5"></th>
               </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
               {isLoading ? (
                 <tr><td colSpan="7" className="p-12 text-center text-gray-400 font-black animate-pulse">Loading Asset Inventory...</td></tr>
               ) : filteredSites?.length === 0 ? (
                 <tr>
                   <td colSpan="7" className="p-20 text-center">
                     <div className="flex flex-col items-center gap-2 opacity-20">
                        <Filter size={48} />
                        <p className="text-sm font-black uppercase tracking-widest">No assets found in portfolio</p>
                     </div>
                   </td>
                 </tr>
               ) : filteredSites?.map(site => (
                 <tr key={site.site_id} className="hover:bg-gray-50/30 transition-all group">
                    <td className="px-8 py-6">
                       <div className="flex items-center gap-4">
                         <div className="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-green-600 font-black text-xs">
                            {site.name.charAt(0)}
                         </div>
                         <div>
                            <p className="font-black text-gray-800 text-sm">{site.name}</p>
                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-1">
                              <MapPin size={10} /> {site.country}
                            </p>
                         </div>
                       </div>
                    </td>
                    <td className="px-6 py-6">
                       <p className="text-xs font-bold text-gray-600 leading-tight max-w-[200px] truncate">{site.activities?.[0]}</p>
                    </td>
                    <td className="px-6 py-6 text-center">
                       {site.tnfd_priority ? (
                         <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 border border-orange-100 text-orange-600 rounded-full text-[9px] font-black uppercase">
                            <AlertTriangle size={10} /> Priority
                         </div>
                       ) : (
                         <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 text-gray-400 rounded-full text-[9px] font-black uppercase">
                            Standard
                         </div>
                       )}
                    </td>
                    <td className="px-6 py-6 text-center">
                       <div className="inline-block text-sm font-black text-gray-800">
                          {Math.round(site.priority_score)}
                       </div>
                       <p className="text-[8px] font-black text-gray-300 uppercase tracking-tighter">{site.priority_tier}</p>
                    </td>
                    <td className="px-6 py-6">
                       <div className="flex justify-center gap-1.5">
                          {site.pressures?.map((p, i) => <ScoreChip key={i} level={p.level} label={p.label} />)}
                       </div>
                    </td>
                    <td className="px-6 py-6">
                       <div className="flex justify-center gap-1.5">
                          {site.dependencies?.map((d, i) => <ScoreChip key={i} level={d.level} label={d.label} />)}
                       </div>
                    </td>
                    <td className="px-6 py-6 text-right whitespace-nowrap">
                       <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => handleDeleteSite(site.site_id)}
                            className="p-2.5 rounded-xl hover:bg-red-50 transition-all text-gray-300 hover:text-red-500 inline-flex items-center justify-center"
                            title="Delete Site"
                          >
                             <Trash2 size={16} />
                          </button>
                          <Link to={`/sites/${site.site_id}`} className="p-2.5 rounded-xl hover:bg-gray-100 transition-all inline-flex items-center justify-center text-gray-300 hover:text-gray-800">
                             <ChevronRight size={20} />
                          </Link>
                       </div>
                    </td>
                 </tr>
               ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ScoreChip({ level, label }) {
  const COLORS = {
    VL: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    L: 'bg-yellow-200 text-yellow-800 border-yellow-400',
    M: 'bg-orange-100 text-orange-700 border-orange-300',
    H: 'bg-red-50 text-red-600 border-red-200',
    VH: 'bg-red-100 text-red-700 border-red-300'
  };
  return (
    <div 
      title={`${label}: ${level}`}
      className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black border transition-transform hover:scale-110 cursor-help shadow-sm",
        COLORS[level] || 'bg-gray-50 text-gray-400 border-gray-200'
      )}
    >
      {level || '-'}
    </div>
  );
}

