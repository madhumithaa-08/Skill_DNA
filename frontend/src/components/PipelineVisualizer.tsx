import React, { useEffect, useState } from 'react';
import { Eye, HelpCircle, Building2, GraduationCap, CheckCircle2, Loader2, ArrowRight, Zap, PackageOpen, Clock } from 'lucide-react';
import { PipelineStage } from '../types';

interface PipelineVisualizerProps {
  currentStage: PipelineStage;
  activeStatusText?: string;
  isDemo?: boolean;
  pipelineSummary?: {
    stepsFound?: number;
    gapsFound?: number;
    questionsGenerated?: number;
    elapsedMs?: number;
  };
}

const AGENTS = [
  {
    id: 'observer' as PipelineStage,
    name: 'Observer Agent',
    role: 'Extracts visible steps & tacit gaps',
    icon: Eye,
    gradient: 'from-blue-600 to-indigo-600',
    badge: 'Stage 1',
  },
  {
    id: 'interviewer' as PipelineStage,
    name: 'Interviewer Agent',
    role: 'Formulates tacit knowledge questions',
    icon: HelpCircle,
    gradient: 'from-indigo-600 to-purple-600',
    badge: 'Stage 2',
  },
  {
    id: 'knowledge_architect' as PipelineStage,
    name: 'Knowledge Architect',
    role: 'Synthesizes Skill Fingerprint DNA',
    icon: Building2,
    gradient: 'from-purple-600 to-rose-700',
    badge: 'Stage 3',
  },
  {
    id: 'curriculum' as PipelineStage,
    name: 'Curriculum Agent',
    role: 'Builds masterclass practice & quiz',
    icon: GraduationCap,
    gradient: 'from-rose-700 to-amber-600',
    badge: 'Stage 4',
  },
];

const STAGE_ORDER: PipelineStage[] = ['observer', 'interviewer', 'knowledge_architect', 'curriculum'];

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({
  currentStage,
  activeStatusText,
  isDemo,
  pipelineSummary,
}) => {
  const isIdle = currentStage === 'idle';
  const isComplete = currentStage === 'complete';
  const currentIndex = isIdle ? -1 : isComplete ? 4 : STAGE_ORDER.indexOf(currentStage);

  const [elapsedSec, setElapsedSec] = useState(0);
  const [startTime] = useState(() => Date.now());

  useEffect(() => {
    if (isIdle || isComplete) return;
    const timer = setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [isIdle, isComplete, startTime]);

  if (isIdle) {
    return (
      <div className="hud-glass rounded-2xl px-5 py-3 mb-8 flex items-center justify-between gap-3 text-stone-300">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            {AGENTS.map((a) => (
              <div key={a.id} className="w-2 h-2 rounded-full bg-white/20" />
            ))}
          </div>
          <span className="text-xs font-bold uppercase tracking-widest text-craft-amber-400">
            Strands Multi-Agent Orchestration
          </span>
          <span className="hidden sm:flex items-center gap-1.5 text-xs text-stone-400">
            {AGENTS.map((a, i) => (
              <React.Fragment key={a.id}>
                <span>{a.name}</span>
                {i < AGENTS.length - 1 && <ArrowRight className="w-3 h-3 text-stone-600" />}
              </React.Fragment>
            ))}
          </span>
        </div>
        <span className="text-xs text-stone-400 font-mono">Pipeline Idle</span>
      </div>
    );
  }

  return (
    <div className="hud-glass rounded-3xl p-5 sm:p-6 mb-8 transition-all">
      {/* Header row */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-5 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className={`w-2.5 h-2.5 rounded-full ${isComplete ? 'bg-emerald-400' : 'bg-craft-amber-400 animate-ping'}`} />
          <span className="text-xs font-bold uppercase tracking-widest text-white">
            Strands Multi-Agent Orchestration Active
          </span>
          {isComplete && (
            isDemo ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-400/20 text-amber-300 border border-amber-400/30">
                <PackageOpen className="w-3 h-3" /> Demo Mode
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <Zap className="w-3 h-3" /> Live Bedrock Nova Pro
              </span>
            )
          )}
        </div>

        <div className="flex items-center gap-2">
          {!isComplete && (
            <span className="inline-flex items-center gap-1 text-xs font-medium text-stone-400">
              <Clock className="w-3.5 h-3.5" /> {elapsedSec}s
            </span>
          )}
          {activeStatusText && (
            <span className="inline-flex items-center gap-2 text-xs font-bold text-craft-amber-300 bg-craft-amber-400/15 px-3 py-1 rounded-full border border-craft-amber-400/30">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              {activeStatusText}
            </span>
          )}
        </div>
      </div>

      {/* Agents grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {AGENTS.map((agent, idx) => {
          const isCurrent = currentStage === agent.id;
          const isDone = currentIndex > idx;
          const Icon = agent.icon;

          return (
            <div
              key={agent.id}
              className={`rounded-2xl p-4 border transition-all duration-300 ${
                isCurrent
                  ? 'border-craft-amber-400 bg-white/10 shadow-lg ring-2 ring-craft-amber-400/30 scale-102'
                  : isDone
                  ? 'border-emerald-500/30 bg-emerald-950/20 text-stone-200'
                  : 'border-white/5 bg-white/5 text-stone-400 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-md ${
                    isCurrent
                      ? 'bg-gradient-to-br from-craft-amber-500 to-craft-crimson-600'
                      : isDone
                      ? 'bg-emerald-600'
                      : 'bg-white/10'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-stone-400 px-1.5 py-0.5 rounded bg-white/10">
                    {agent.badge}
                  </span>
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-craft-amber-400 animate-spin" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-stone-600" />
                  )}
                </div>
              </div>

              <h4 className={`text-sm font-bold font-serif-heading mb-1 ${isCurrent ? 'text-craft-amber-200' : 'text-white'}`}>
                {agent.name}
              </h4>
              <p className="text-xs text-stone-400 leading-snug">
                {agent.role}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
