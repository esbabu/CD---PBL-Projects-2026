import React from 'react';
import { Terminal, Code2, Shield, MessageSquare } from 'lucide-react';
import { ActiveTab } from '../../features/run/runTypes';

interface ResultsTabsProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  hasOptimizedCode: boolean;
  isUnverified?: boolean;
  securityFindingsCount: number;
  messagesCount: number;
  isStale?: boolean;
}

export const ResultsTabs: React.FC<ResultsTabsProps> = ({
  activeTab,
  onTabChange,
  hasOptimizedCode,
  isUnverified = false,
  securityFindingsCount,
  messagesCount,
  isStale = false,
}) => {
  const tabs = [
    {
      id: 'output' as ActiveTab,
      label: 'Output',
      icon: Terminal,
      badge: null,
    },
    {
      id: 'optimized_code' as ActiveTab,
      label: 'Optimized Code',
      icon: Code2,
      badge: hasOptimizedCode ? (isUnverified ? 'Analysis Only' : 'Ready') : null,
      badgeClass: isUnverified ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-700',
    },
    {
      id: 'security' as ActiveTab,
      label: 'Security',
      icon: Shield,
      badge: securityFindingsCount > 0 ? `${securityFindingsCount}` : null,
      badgeClass: 'bg-amber-100 text-amber-800',
    },
    {
      id: 'messages' as ActiveTab,
      label: 'Messages',
      icon: MessageSquare,
      badge: messagesCount > 0 ? `${messagesCount}` : null,
      badgeClass: 'bg-slate-100 text-slate-600',
    },
  ];

  return (
    <div className="h-10 border-b border-slate-200 dark:border-slate-800 px-3 flex items-center justify-between bg-slate-50/80 dark:bg-slate-900 shrink-0">
      <div className="flex items-center gap-1.5">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-blue-100 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 shadow-2xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-200/50 dark:hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.badge && (
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full ${
                    tab.badgeClass || 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {isStale && (
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          Results stale — source modified
        </span>
      )}
    </div>
  );
};
