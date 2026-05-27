import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, List, HelpCircle } from 'lucide-react';
import darukaaLogo from '../assets/darukaa_logo.png';
import { cn } from '../lib/utils';

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Portfolio', icon: <LayoutDashboard size={18} /> },
    { path: '/sites', label: 'Inventory', icon: <List size={18} /> },
  ];

  const bottomItems = [
    { path: '/help', label: 'Support', icon: <HelpCircle size={18} /> },
  ];

  return (
    <div className="flex h-screen w-full bg-[#f8faf8] text-gray-800 font-sans">
      {/* Sidebar */}
      <aside className="w-72 bg-white border-r border-gray-100 flex flex-col shadow-[10px_0_30px_rgba(0,0,0,0.02)] z-50">
        <div className="p-8 pb-10">
          <img src={darukaaLogo} alt="Logo" className="h-8 w-fit object-contain mb-8 select-none" />
          <div className="space-y-1">

             <p className="text-[10px] font-black text-green-800/30 uppercase tracking-[0.2em] mb-4">Core Platform</p>
             <nav className="space-y-2">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={cn(
                        "flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300",
                        isActive 
                          ? "bg-green-600 text-white shadow-xl shadow-green-100 font-black scale-105" 
                          : "text-gray-400 hover:text-gray-800 hover:bg-gray-50"
                      )}
                    >
                      {item.icon}
                      <span className="text-xs uppercase tracking-widest">{item.label}</span>
                    </Link>
                  );
                })}
             </nav>
          </div>
        </div>
        
        <div className="mt-auto p-8 border-t border-gray-50">
           <nav className="space-y-4">
              {bottomItems.map(item => (
                <div key={item.label} className="flex items-center gap-4 px-5 text-gray-400 hover:text-gray-800 cursor-pointer transition-colors">
                   {item.icon}
                   <span className="text-[10px] font-black uppercase tracking-widest">{item.label}</span>
                </div>
              ))}
           </nav>
        </div>
      </aside>


      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-[#f8faf8]">
        <div className="p-12 h-full max-w-[1400px] mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
