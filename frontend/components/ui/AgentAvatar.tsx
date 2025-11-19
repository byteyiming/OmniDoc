'use client';

import React from 'react';
import { Cpu, PenTool, CheckCircle, Search, Shield, Zap, Code, LucideIcon } from 'lucide-react';

export type AgentRole = 'architect' | 'writer' | 'critic' | 'researcher' | 'security' | 'default';

interface AgentAvatarProps {
  role?: AgentRole;
  size?: 'sm' | 'md' | 'lg';
  pulsing?: boolean;
  className?: string;
}

const AGENT_CONFIG: Record<AgentRole, { color: string; icon: LucideIcon }> = {
  architect: { color: 'bg-blue-500', icon: Cpu },
  writer: { color: 'bg-pink-500', icon: PenTool },
  critic: { color: 'bg-amber-500', icon: CheckCircle },
  researcher: { color: 'bg-purple-500', icon: Search },
  security: { color: 'bg-emerald-500', icon: Shield },
  default: { color: 'bg-indigo-500', icon: Zap },
};

export function AgentAvatar({ 
  role = 'default', 
  size = 'md', 
  pulsing = false,
  className = ''
}: AgentAvatarProps) {
  const config = AGENT_CONFIG[role] || AGENT_CONFIG.default;
  const Icon = config.icon;
  
  const sizeClasses = {
    sm: "w-8 h-8 p-1.5",
    md: "w-12 h-12 p-2.5",
    lg: "w-16 h-16 p-4"
  };
  
  return (
    <div className={`relative ${className}`}>
      <div className={`
        rounded-full flex items-center justify-center shadow-lg text-white
        ${config.color} 
        ${sizeClasses[size]}
        ${pulsing ? 'animate-pulse-ring' : ''}
      `}>
        <Icon className="w-full h-full" />
      </div>
      {/* Status Dot */}
      <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 border-2 border-[#0B0F19] rounded-full"></div>
    </div>
  );
}

