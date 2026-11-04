import React, { useState } from 'react';
import {
  Dna,
  ShieldCheck,
  MapPin,
  Clock,
  Layers,
  GitBranch,
  Package,
  Award,
  AlertTriangle,
  Copy,
  Check,
  Download,
  Lightbulb,
  ExternalLink,
  Flame,
  Grid,
  ArrowRight,
} from 'lucide-react';
import { SkillFingerprint } from '../types';

interface SkillFingerprintViewProps {
  fingerprint: SkillFingerprint | null;
  onGoToLearner: () => void;
}

export const SkillFingerprintView: React.FC<SkillFingerprintViewProps> = ({
  fingerprint,
  onGoToLearner,
}) => {
  const [activeTab, setActiveTab] = useState<'techniques' | 'decisions' | 'pattern' | 'materials' | 'mastery' | 'json'>('techniques');
  const [copied, setCopied] = useState(false);
  const [selectedDot, setSelectedDot] = useState<{ row: number; col: number } | null>({ row: 3, col: 4 });

  if (!fingerprint) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 hud-glass rounded-3xl p-8">
        <div className="w-16 h-16 rounded-2xl bg-amber-400/10 text-craft-amber-400 mx-auto flex items-center justify-center mb-4 border border-craft-amber-400/30">
          <Dna className="w-8 h-8 animate-pulse text-craft-amber-400" />
        </div>
        <h3 className="text-xl font-bold text-white font-serif-heading">
          No Skill Fingerprint Crystallized Yet
        </h3>
        <p className="text-sm text-stone-400 max-w-md mx-auto mt-2 leading-relaxed">
          Describe a craft in <strong>Stage 01: Artisan Capture</strong> and answer the interview questions, or load a pre-built demo from the top bar.
        </p>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(fingerprint, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(fingerprint, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${fingerprint.craft_name.toLowerCase().replace(/\s+/g, '_')}_fingerprint.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      
      {/* Living Heritage Temple Header */}
      <div className="hud-glass-amber rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2.5">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-craft-amber-400 to-amber-300 text-craft-indigo-950 shadow-xs">
                <Dna className="w-3.5 h-3.5" />
                Skill DNA v{fingerprint.version}
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-stone-200 border border-white/15">
                <MapPin className="w-3 h-3 text-craft-amber-400" />
                {fingerprint.craft_origin}
              </span>
              {fingerprint.artisan_approved && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Artisan Approved & Attributed
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-4xl font-bold font-serif-heading tracking-tight mb-2 text-white">
              {fingerprint.craft_name}
            </h1>
            <p className="text-stone-300 text-xs sm:text-sm max-w-2xl font-sans">
              Captured from Master Artisan: <strong className="text-white">{fingerprint.artisan_name}</strong> • {fingerprint.craft_heritage}
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5 shrink-0">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/15 transition-all cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy JSON'}
            </button>
            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/15 transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Download .json
            </button>
            <button
              onClick={onGoToLearner}
              className="inline-flex items-center gap-2 px-5 py-2.5 text-xs font-bold bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 text-craft-indigo-950 rounded-xl shadow-lg transition-all cursor-pointer"
            >
              Enter Apprentice Masterclass
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Cultural Significance Quote */}
        {fingerprint.cultural_significance && (
          <div className="mt-6 pt-6 border-t border-white/10">
            <div className="flex items-start gap-3">
              <Flame className="w-5 h-5 text-craft-amber-400 shrink-0 mt-0.5" />
              <blockquote className="text-xs sm:text-sm text-stone-200 italic leading-relaxed font-serif max-w-4xl">
                "{fingerprint.cultural_significance}"
              </blockquote>
            </div>
          </div>
        )}
      </div>

      {/* Metrics Row (HUD Glass) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="hud-glass p-5 rounded-2xl">
          <div className="flex items-center justify-between text-stone-400 mb-1.5">
            <span className="text-xs uppercase font-bold tracking-wider">Techniques</span>
            <Layers className="w-4 h-4 text-craft-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white font-serif-heading">
            {fingerprint.techniques.length}
          </div>
          <span className="text-xs text-stone-400 font-medium">Documented stages</span>
        </div>

        <div className="hud-glass p-5 rounded-2xl">
          <div className="flex items-center justify-between text-stone-400 mb-1.5">
            <span className="text-xs uppercase font-bold tracking-wider">Decisions</span>
            <GitBranch className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-white font-serif-heading">
            {fingerprint.decisions.length}
          </div>
          <span className="text-xs text-stone-400 font-medium">Judgment "Why" points</span>
        </div>

        <div className="hud-glass p-5 rounded-2xl">
          <div className="flex items-center justify-between text-stone-400 mb-1.5">
            <span className="text-xs uppercase font-bold tracking-wider">Materials</span>
            <Package className="w-4 h-4 text-craft-amber-400" />
          </div>
          <div className="text-3xl font-bold text-white font-serif-heading">
            {fingerprint.materials.length}
          </div>
          <span className="text-xs text-stone-400 font-medium">Natural earth elements</span>
        </div>

        <div className="hud-glass p-5 rounded-2xl">
          <div className="flex items-center justify-between text-stone-400 mb-1.5">
            <span className="text-xs uppercase font-bold tracking-wider">Mastery Skills</span>
            <Award className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white font-serif-heading">
            {fingerprint.mastery_requirements.length}
          </div>
          <span className="text-xs text-stone-400 font-medium">Tactile benchmarks</span>
        </div>
      </div>

      {/* Holographic Tabs */}
      <div className="border-b border-white/10 hud-glass rounded-t-2xl px-5 pt-3.5 flex gap-2 overflow-x-auto">
        {[
          { id: 'techniques', label: 'Techniques Roadmap', icon: Layers },
          { id: 'decisions', label: 'The Master\'s Secret ("Why")', icon: GitBranch },
          { id: 'pattern', label: 'Geometric Resist Pattern', icon: Grid },
          { id: 'materials', label: 'Materials of the Earth', icon: Package },
          { id: 'mastery', label: 'Mastery & Pitfalls', icon: Award },
          { id: 'json', label: 'Skill DNA JSON', icon: Dna },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`inline-flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-bold rounded-t-xl transition-all border-b-2 whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'border-craft-amber-400 text-craft-amber-300 bg-white/10'
                  : 'border-transparent text-stone-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Techniques */}
      {activeTab === 'techniques' && (
        <div className="hud-glass rounded-b-2xl p-6 sm:p-8 space-y-4">
          {fingerprint.techniques.map((tech, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-craft-amber-400/40 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                <div className="flex items-center gap-2.5">
                  <span className="w-8 h-8 rounded-xl bg-purple-900/60 border border-purple-500/40 text-craft-amber-300 text-xs font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-white font-serif-heading">
                    {tech.name}
                  </h3>
                  <span className="text-xs text-stone-400 font-medium">({tech.stage})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-stone-300 bg-white/10 px-2.5 py-1 rounded-lg">
                    <Clock className="w-3.5 h-3.5 text-craft-amber-400" />
                    {tech.duration_estimate}
                  </span>
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
                      tech.difficulty === 'advanced'
                        ? 'bg-rose-950/60 text-rose-300 border border-rose-800/60'
                        : tech.difficulty === 'intermediate'
                        ? 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                        : 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                    }`}
                  >
                    {tech.difficulty}
                  </span>
                </div>
              </div>

              <p className="text-sm text-stone-300 leading-relaxed mb-4">
                {tech.description}
              </p>

              {tech.tips && tech.tips.length > 0 && (
                <div className="bg-amber-500/10 rounded-xl p-4 border border-amber-400/30">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300 mb-2">
                    <Lightbulb className="w-4 h-4 text-craft-amber-400" />
                    Artisan's Tactile Advice & Sensory Checkpoints:
                  </div>
                  <ul className="text-xs sm:text-sm text-amber-100 space-y-1.5 list-disc pl-5">
                    {tech.tips.map((tip, tipIdx) => (
                      <li key={tipIdx} className="leading-relaxed">{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Decisions Matrix */}
      {activeTab === 'decisions' && (
        <div className="hud-glass rounded-b-2xl p-6 sm:p-8 space-y-6">
          <div className="pb-2 border-b border-white/10">
            <h3 className="text-lg font-bold text-white font-serif-heading">
              The Master's Secret: Intuition vs Amateur Mistakes
            </h3>
            <p className="text-xs text-stone-400 mt-1">
              Every decision point captures the exact experiential rationale passed through generations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {fingerprint.decisions.map((dec, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-craft-amber-400/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <h4 className="text-base font-bold text-white font-serif-heading">
                      {dec.decision_point}
                    </h4>
                    <span className="text-xs px-3 py-1 rounded-full font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shrink-0">
                      Master Choice: {dec.artisan_choice}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-stone-400 mb-4">
                    <span className="font-bold text-stone-300">Options Considered:</span>
                    {dec.options.map((opt, optIdx) => (
                      <span
                        key={optIdx}
                        className={`px-2 py-0.5 rounded-md text-xs ${
                          opt.toLowerCase() === dec.artisan_choice.toLowerCase()
                            ? 'bg-emerald-500 text-black font-extrabold'
                            : 'bg-white/10 text-stone-400 font-medium'
                        }`}
                      >
                        {opt}
                      </span>
                    ))}
                  </div>

                  <div className="bg-black/40 p-4 rounded-xl border border-white/10 text-xs sm:text-sm text-stone-200 leading-relaxed">
                    <strong className="text-craft-amber-300 block mb-1.5 font-sans">
                      💡 Artisan Reasoning & Tacit Judgment:
                    </strong>
                    {dec.reasoning}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Geometric Resist Pattern Visualizer */}
      {activeTab === 'pattern' && (
        <div className="hud-glass rounded-b-2xl p-6 sm:p-8">
          <div className="max-w-2xl mx-auto text-center mb-6">
            <span className="text-xs font-bold uppercase tracking-wider text-craft-amber-300 bg-craft-amber-400/15 px-2.5 py-1 rounded-full border border-craft-amber-400/30">
              Interactive Motif Canvas
            </span>
            <h3 className="text-xl font-bold text-white font-serif-heading mt-2">
              Sungudi Knot Resist Grid (Simulated Tie-Dye)
            </h3>
            <p className="text-xs text-stone-400 mt-1">
              Click on any white knot circle below to inspect the tactile knot-tension parameters encoded at that coordinate.
            </p>
          </div>

          <div className="flex flex-col lg:flex-row items-center justify-center gap-8 py-4">
            {/* SVG Canvas */}
            <div className="p-6 rounded-3xl bg-[#581c24] shadow-2xl border-4 border-craft-amber-400/40 relative">
              <svg width="280" height="280" viewBox="0 0 280 280" className="rounded-xl">
                <rect width="280" height="280" fill="#7f1d1d" rx="12" />
                {Array.from({ length: 7 }).map((_, r) =>
                  Array.from({ length: 7 }).map((_, c) => {
                    const isSelected = selectedDot?.row === r && selectedDot?.col === c;
                    const cx = 25 + c * 38;
                    const cy = 25 + r * 38;
                    return (
                      <g
                        key={`${r}-${c}`}
                        onClick={() => setSelectedDot({ row: r, col: c })}
                        className="cursor-pointer group"
                      >
                        <circle
                          cx={cx}
                          cy={cy}
                          r={isSelected ? 14 : 10}
                          fill="#fef2f2"
                          opacity={isSelected ? '0.95' : '0.85'}
                          className="transition-all duration-200 group-hover:scale-110"
                        />
                        <circle
                          cx={cx}
                          cy={cy}
                          r={isSelected ? 6 : 4}
                          fill="#ffffff"
                        />
                        {isSelected && (
                          <circle
                            cx={cx}
                            cy={cy}
                            r={18}
                            fill="none"
                            stroke="#fbbf24"
                            strokeWidth="2"
                            strokeDasharray="4 2"
                            className="animate-spin"
                            style={{ transformOrigin: `${cx}px ${cy}px` }}
                          />
                        )}
                      </g>
                    );
                  })
                )}
              </svg>
            </div>

            {/* Dot Inspector */}
            {selectedDot && (
              <div className="hud-glass p-6 rounded-2xl max-w-sm w-full">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-craft-amber-300">
                    Knot Coordinate ({selectedDot.row + 1}, {selectedDot.col + 1})
                  </span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    Resist Barrier Intact
                  </span>
                </div>
                <h4 className="text-base font-bold text-white font-serif-heading mb-2">
                  Bandhani Pinch at 1.5 cm Spacing
                </h4>
                <div className="space-y-2 text-xs text-stone-300">
                  <div className="flex justify-between border-b border-white/10 pb-1.5">
                    <span className="text-stone-400">Pinch Peak:</span>
                    <strong className="font-mono text-craft-amber-300">3.5 mm</strong>
                  </div>
                  <div className="flex justify-between border-b border-white/10 pb-1.5">
                    <span className="text-stone-400">Thread Wraps:</span>
                    <strong className="font-mono text-craft-amber-300">3 firm turns + double knot</strong>
                  </div>
                  <div className="flex justify-between border-b border-white/10 pb-1.5">
                    <span className="text-stone-400">Dye Resistance:</span>
                    <strong className="text-emerald-400">100% (Crisp white circle)</strong>
                  </div>
                  <div className="flex justify-between pb-1">
                    <span className="text-stone-400">Audible Release:</span>
                    <strong className="italic text-stone-200">Soft "snap" on scissor cut</strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Materials of the Earth */}
      {activeTab === 'materials' && (
        <div className="hud-glass rounded-b-2xl p-6 sm:p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {fingerprint.materials.map((mat, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:border-craft-amber-400/40 transition-all"
              >
                <div className="flex items-center gap-2 mb-2.5">
                  <Package className="w-5 h-5 text-craft-amber-400" />
                  <h4 className="text-base font-bold text-white font-serif-heading">
                    {mat.name}
                  </h4>
                </div>
                <p className="text-xs sm:text-sm text-stone-300 leading-relaxed mb-3">
                  {mat.description}
                </p>
                <div className="text-xs text-stone-400 border-t border-white/10 pt-2.5">
                  <span className="font-bold text-stone-200">Origin / Source:</span> {mat.source}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Mastery & Common Mistakes */}
      {activeTab === 'mastery' && (
        <div className="hud-glass rounded-b-2xl p-6 sm:p-8 space-y-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-rose-400 mb-3.5">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              Common Learner Pitfalls & Artisan Corrections
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {fingerprint.common_mistakes.map((mistake, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-rose-950/20 border border-rose-800/40">
                  <h4 className="text-xs font-bold text-rose-300 mb-1.5 flex items-center gap-1.5">
                    ⚠️ {mistake.mistake}
                  </h4>
                  <p className="text-xs text-rose-200/90 mb-3 leading-relaxed">
                    <strong>Consequence:</strong> {mistake.consequence}
                  </p>
                  <p className="text-xs text-stone-300 bg-black/40 p-3 rounded-xl border border-white/10 leading-relaxed">
                    <strong>Artisan Correction:</strong> {mistake.correction}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-white/10">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3.5">
              <Award className="w-4 h-4 text-emerald-400" />
              Mastery Benchmarks & Demonstrations
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {fingerprint.mastery_requirements.map((req, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-800/40">
                  <h4 className="text-xs font-bold text-emerald-300 mb-1.5 flex items-center gap-1.5">
                    <Check className="w-4 h-4 text-emerald-400" />
                    {req.skill}
                  </h4>
                  <p className="text-xs text-stone-300 bg-black/40 p-3 rounded-xl border border-white/10 mt-2 leading-relaxed">
                    <strong>Benchmark Test:</strong> {req.how_to_demonstrate}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: Raw JSON */}
      {activeTab === 'json' && (
        <div className="hud-glass rounded-b-2xl p-6 text-stone-200">
          <pre className="text-xs font-mono overflow-x-auto max-h-[500px] leading-relaxed p-4 bg-black/60 rounded-xl border border-white/10">
            {JSON.stringify(fingerprint, null, 2)}
          </pre>
        </div>
      )}

    </div>
  );
};
