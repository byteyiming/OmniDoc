import Link from 'next/link';
import {
  LayoutDashboard,
  FolderKanban,
  Bot,
  Settings,
  Sparkles,
} from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="w-64 flex-shrink-0 bg-sidebar p-6 flex flex-col">
      {/* Logo */}
      <div className="flex items-center space-x-3 mb-10">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-secondary text-white shadow-lg">
          <Sparkles className="h-6 w-6" />
        </div>
        <span className="text-xl font-bold text-white">OmniDoc</span>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1">
        <ul className="space-y-2">
          <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" href="/dashboard" active />
          <NavItem icon={<FolderKanban size={20} />} label="Projects" href="/projects" />
          <NavItem icon={<Bot size={20} />} label="Agents" href="/agents" />
          <NavItem icon={<Settings size={20} />} label="Settings" href="/settings" />
        </ul>
      </nav>

      {/* User Profile / Credits */}
      <div className="mt-auto">
        <div className="bg-card p-4 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-400 to-blue-500" />
            <div>
              <p className="font-semibold text-white">Alex Chen</p>
              <p className="text-xs text-gray-400">Pro Plan</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>Credits</span>
              <span>850/1000</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className="bg-primary h-1.5 rounded-full"
                style={{ width: '85%' }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  active?: boolean;
}

const NavItem = ({ icon, label, href, active = false }: NavItemProps) => {
  const baseClasses = 'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors';
  const activeClasses = 'bg-primary/20 text-white font-semibold';
  const inactiveClasses = 'text-gray-400 hover:bg-white/5 hover:text-white';

  return (
    <li>
      <Link href={href} className={`${baseClasses} ${active ? activeClasses : inactiveClasses}`}>
        {icon}
        <span>{label}</span>
      </Link>
    </li>
  );
};

export default Sidebar;
