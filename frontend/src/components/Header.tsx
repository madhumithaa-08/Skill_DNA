import React from 'react';
import { Sparkles, Dna, History, Zap, PackageOpen, ChevronRight, ArrowRight } from 'lucide-react';

interface HeaderProps {
  onLoadDemo: () => void;
  onOpenArchives: () => void;
  isDemoLoaded: boolean;
  hasFingerprint: boolean;
  isLiveAI: boolean;
  activeTab: 'artisan' | 'fingerprint' | 'learner';
  setActiveTab: (tab: 'artisan' | 'fingerprint' | 'learner') => void;
}

const STAGES = [
  { id: 'artisan' as const, num: '01', title: 'Artisan Capture', icon: '🎨' },
  { id: 'fingerprint' as const, num: '02', title: 'Skill DNA', icon: '🧬' },
  { id: 'learner' as const, num: '03', title: 'Apprentice Masterclass', icon: '📚' },
];

export const Header: React.FC<HeaderProps> = ({
  onLoadDemo,
  onOpenArchives,
  isDemoLoaded,
  hasFingerprint,
  isLiveAI,
  activeTab,
  setActiveTab,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-[#080614]/85 backdrop-blur-2xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20 gap-4">

          {/* Brand Logo & Illuminated Helix */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="relative w-11 h-11 rounded-2xl bg-gradient-to-br from-purple-900 via-craft-crimson-800 to-craft-amber-600 flex items-center justify-center shadow-lg shadow-purple-950/50 ring-1 ring-craft-amber-400/40">
              <Dna className="w-6 h-6 text-craft-amber-200 animate-pulse" />
              {isLiveAI && (
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#080614] animate-ping" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl sm:text-2xl font-bold tracking-tight text-white font-serif-heading">
                  SKILL DNA
                </span>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold tracking-widest uppercase bg-craft-amber-400/15 text-craft-amber-300 border border-craft-amber-400/30">
                  GI Heritage AI
                </span>
              </div>
              <p className="text-[11px] text-stone-400 italic hidden sm:block">
                Preserving the unspoken touch in hands
              </p>
            </div>
          </div>

          {/* Centered Seamless 3-Stage Cycle Stepper */}
          <nav className="flex items-center p-1 rounded-2xl bg-black/40 border border-white/10 shadow-inner">
            {STAGES.map((stage, idx) => {
              const isActive = activeTab === stage.id;
              return (
                <React.Fragment key={stage.id}>
                  <button
                    onClick={() => setActiveTab(stage.id)}
                    className={`relative px-3.5 sm:px-5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-300 flex items-center gap-2 cursor-pointer ${
                      isActive
                        ? 'bg-gradient-to-r from-craft-amber-500 to-craft-amber-400 text-craft-indigo-950 shadow-lg shadow-amber-500/25 font-bold scale-102'
                        : 'text-stone-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <span className="opacity-75 text-[10px] font-mono">{stage.num}</span>
                    <span className="text-sm">{stage.icon}</span>
                    <span className="hidden sm:inline whitespace-nowrap">{stage.title}</span>
                    {stage.id === 'fingerprint' && hasFingerprint && !isActive && (
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    )}
                  </button>
                  {idx < STAGES.length - 1 && (
                    <ChevronRight className="w-3.5 h-3.5 text-stone-600 hidden sm:block mx-0.5 shrink-0" />
                  )}
                </React.Fragment>
              );
            })}
          </nav>

          {/* Quick Actions */}
          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={onLoadDemo}
              title="Load pre-built Madurai Sungudi masterclass"
              className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                isDemoLoaded
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40'
                  : 'bg-gradient-to-r from-purple-700 to-indigo-800 hover:from-purple-600 hover:to-indigo-700 text-white border-white/15 shadow-md shadow-purple-950/40'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-craft-amber-300" />
              <span className="hidden lg:inline">
                {isDemoLoaded ? 'Demo Loaded' : 'Load Demo'}
              </span>
            </button>

            <button
              onClick={onOpenArchives}
              className="p-2 text-stone-400 hover:text-white hover:bg-white/10 rounded-xl border border-white/10 transition-colors cursor-pointer"
              title="Saved Fingerprints Archive"
            >
              <History className="w-4 h-4" />
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
