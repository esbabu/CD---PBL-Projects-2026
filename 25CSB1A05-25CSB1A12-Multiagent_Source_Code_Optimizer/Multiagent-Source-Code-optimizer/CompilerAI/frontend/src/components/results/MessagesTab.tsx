import React from 'react';
import { MessageSquare, AlertTriangle, AlertCircle, Info, Sparkles } from 'lucide-react';
import { RunMessage } from '../../features/run/runTypes';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

interface MessagesTabProps {
  messages: RunMessage[];
}

export const MessagesTab: React.FC<MessagesTabProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-slate-400">
        <MessageSquare className="w-8 h-8 mb-2 stroke-1" />
        <p className="text-xs font-medium text-slate-500">
          No system messages recorded.
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Execution lifecycles, demo mode notices, and fallback logs will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full p-4 overflow-y-auto space-y-2 bg-slate-50/50">
      {messages.map((msg) => {
        let icon = <Info className="w-3.5 h-3.5 text-blue-500" />;
        let borderClass = 'border-slate-200 bg-white';

        if (msg.category === 'warning') {
          icon = <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />;
          borderClass = 'border-amber-200 bg-amber-50/40';
        } else if (msg.category === 'error') {
          icon = <AlertCircle className="w-3.5 h-3.5 text-rose-500" />;
          borderClass = 'border-rose-200 bg-rose-50/40';
        } else if (msg.category === 'demo') {
          icon = <Sparkles className="w-3.5 h-3.5 text-indigo-500" />;
          borderClass = 'border-indigo-100 bg-indigo-50/30';
        }

        const formattedTime = new Date(msg.timestamp).toLocaleTimeString();

        return (
          <div
            key={msg.id}
            className={`p-2.5 rounded-xl border flex items-start gap-3 shadow-2xs ${borderClass}`}
          >
            <div className="mt-0.5 shrink-0">{icon}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  {msg.category}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {formattedTime}
                </span>
              </div>
              <p className="text-xs text-slate-700 mt-0.5 leading-relaxed">
                {sanitizeVendor(msg.message)}
              </p>
              {msg.details && (
                <pre className="mt-1.5 p-2 bg-slate-100 rounded text-[11px] font-mono text-slate-600 overflow-x-auto whitespace-pre-wrap">
                  {sanitizeVendor(msg.details)}
                </pre>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
