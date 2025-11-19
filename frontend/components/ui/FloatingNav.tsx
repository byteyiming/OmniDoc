'use client';
import { Layers, Zap, Globe, Search } from 'lucide-react';

const NavPill = ({ icon, active }: { icon: React.ReactNode, active?: boolean }) => (
  <button className={`p-3 rounded-full transition-all ${active ? 'bg-white text-black shadow-lg' : 'text-white/60 hover:text-white hover:bg-white/10'}`}>
    {icon}
  </button>
);

const FloatingNav = () => {
  return (
    <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      <div className="flex items-center gap-1 p-1.5 bg-white/10 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl shadow-black/50">
        <NavPill icon={<Layers size={18} />} active />
        <NavPill icon={<Zap size={18} />} />
        <NavPill icon={<Globe size={18} />} />
        <div className="w-px h-4 bg-white/20 mx-2"></div>
        <div className="flex items-center gap-2 px-4 py-2 text-sm text-white/50 cursor-text hover:text-white transition-colors">
          <Search size={14} />
          <span>Type / to search...</span>
        </div>
        <div className="w-px h-4 bg-white/20 mx-2"></div>
         <button className="w-8 h-8 rounded-full bg-gradient-to-tr from-yellow-400 to-fuchsia-600 p-[2px]">
           <img src="https://api.dicebear.com/9.x/avataaars/svg?seed=Alex" alt="User" className="rounded-full bg-black" />
         </button>
      </div>
    </nav>
  );
};

export default FloatingNav;
