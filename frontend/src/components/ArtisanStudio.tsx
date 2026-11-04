import React, { useState } from 'react';
import {
  FileText,
  Search,
  Sparkles,
  Building2,
  CheckCircle2,
  Layers,
  Wrench,
  Package,
  AlertTriangle,
  Mic,
  Thermometer,
  Droplets,
  Fingerprint,
  Feather,
  ChevronDown,
  ChevronUp,
  ArrowRight,
} from 'lucide-react';
import { ObservationData } from '../types';

interface ArtisanStudioProps {
  craftName: string;
  setCraftName: (name: string) => void;
  artisanName: string;
  setArtisanName: (name: string) => void;
  craftDescription: string;
  setCraftDescription: (desc: string) => void;
  onLoadSampleNotes: () => void;
  onGenerateQuestions: () => void;
  isGeneratingQuestions: boolean;
  observation: ObservationData | null;
  questions: string[];
  answers: Record<string, string>;
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  onCreateFingerprint: () => void;
  isCreatingFingerprint: boolean;
  onFillSampleAnswers: () => void;
}

export const ArtisanStudio: React.FC<ArtisanStudioProps> = ({
  craftName,
  setCraftName,
  artisanName,
  setArtisanName,
  craftDescription,
  setCraftDescription,
  onLoadSampleNotes,
  onGenerateQuestions,
  isGeneratingQuestions,
  observation,
  questions,
  answers,
  setAnswers,
  onCreateFingerprint,
  isCreatingFingerprint,
  onFillSampleAnswers,
}) => {
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number | null>(0);
  const [isRecordingMock, setIsRecordingMock] = useState(false);
  const [artisanApproved, setArtisanApproved] = useState(true);

  // Sensory gauges
  const [waterTemp, setWaterTemp] = useState(82);
  const [moistureState, setMoistureState] = useState<'dry' | 'damp' | 'wet'>('damp');
  const [knotTension, setKnotTension] = useState<'loose' | 'firm' | 'tight'>('firm');

  const handleAnswerChange = (question: string, text: string) => {
    setAnswers((prev) => ({
      ...prev,
      [question]: text,
    }));
  };

  const answeredCount = Object.keys(answers).filter(
    (k) => answers[k] && answers[k].trim().length > 0
  ).length;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      
      {/* Studio Header Banner */}
      <div className="hud-glass-amber rounded-3xl p-6 sm:p-8 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 text-craft-amber-400 text-xs font-bold tracking-widest uppercase mb-1.5">
              <Feather className="w-4 h-4" />
              Stage 01 · Tacit Knowledge Capture
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold font-serif-heading text-white">
              The Living Workshop of {artisanName || 'the Master Artisan'}
            </h2>
            <p className="text-stone-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Describe your craft movements and physical touch in your own words. The multi-agent pipeline uncovers
              unspoken sensory judgment and crystallizes the craft DNA.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={() => setIsRecordingMock(!isRecordingMock)}
              className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                isRecordingMock
                  ? 'bg-rose-600 text-white border-rose-500 animate-pulse'
                  : 'bg-white/10 hover:bg-white/15 text-stone-200 border-white/15'
              }`}
            >
              <Mic className="w-4 h-4 text-craft-amber-400" />
              <span>{isRecordingMock ? 'Recording Dialect...' : 'Record Artisan Voice'}</span>
            </button>
            <button
              onClick={onLoadSampleNotes}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 text-craft-indigo-950 shadow-md transition-all cursor-pointer"
            >
              <FileText className="w-4 h-4" />
              <span>Load Sungudi Notes</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tactile Sensory Dials (HUD Glass) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Temperature Dial */}
        <div className="hud-glass rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-bold text-stone-300 mb-2">
            <span className="flex items-center gap-1.5 text-rose-400">
              <Thermometer className="w-4 h-4" />
              Dye Bath Temperature
            </span>
            <span className="text-craft-amber-300 font-mono text-sm font-bold">
              {waterTemp}°C
            </span>
          </div>
          <input
            type="range"
            min="50"
            max="100"
            value={waterTemp}
            onChange={(e) => setWaterTemp(Number(e.target.value))}
            className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer accent-craft-amber-400"
          />
          <div className="flex justify-between text-[11px] text-stone-400 mt-2 font-medium">
            <span>Warm to Wrist (80°C)</span>
            <span className={waterTemp > 90 ? 'text-rose-400 font-bold' : 'text-craft-amber-300'}>
              {waterTemp > 90 ? '⚠️ Boiling (Weakens Silk)' : 'Ideal Sungudi Heat'}
            </span>
          </div>
        </div>

        {/* Moisture Dial */}
        <div className="hud-glass rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-bold text-stone-300 mb-2">
            <span className="flex items-center gap-1.5 text-blue-400">
              <Droplets className="w-4 h-4" />
              Fabric Moisture Level
            </span>
            <span className="text-blue-300 uppercase tracking-wider text-[11px] font-bold">
              {moistureState}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {(['dry', 'damp', 'wet'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMoistureState(m)}
                className={`py-1.5 text-xs font-bold rounded-lg capitalize border transition-all cursor-pointer ${
                  moistureState === m
                    ? 'bg-blue-600 text-white border-blue-400 shadow-md shadow-blue-900/40'
                    : 'bg-white/5 text-stone-400 border-white/10 hover:bg-white/10'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-stone-400 mt-2">
            {moistureState === 'damp'
              ? '✅ Uniformly damp like cool water: absorbs dye evenly'
              : moistureState === 'dry'
              ? '❌ Dry fibres bleed blotchy patterns'
              : '⚠️ Excess water dilutes dye penetration'}
          </p>
        </div>

        {/* Knot Resistance Dial */}
        <div className="hud-glass rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-bold text-stone-300 mb-2">
            <span className="flex items-center gap-1.5 text-craft-amber-400">
              <Fingerprint className="w-4 h-4" />
              Knot Tension Resistance
            </span>
            <span className="text-craft-amber-300 uppercase tracking-wider text-[11px] font-bold">
              {knotTension}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {(['loose', 'firm', 'tight'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setKnotTension(t)}
                className={`py-1.5 text-xs font-bold rounded-lg capitalize border transition-all cursor-pointer ${
                  knotTension === t
                    ? 'bg-craft-amber-500 text-craft-indigo-950 border-craft-amber-300 shadow-md shadow-amber-900/40'
                    : 'bg-white/5 text-stone-400 border-white/10 hover:bg-white/10'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-stone-400 mt-2">
            {knotTension === 'firm'
              ? '✅ 3 tight wraps with pushback: crisp white circle'
              : knotTension === 'loose'
              ? '❌ Dye bleeds through creating grey smudge'
              : '⚠️ Risks cutting the delicate silk threads'}
          </p>
        </div>
      </div>

      {/* Craft Narrative & Form */}
      <div className="hud-glass rounded-3xl p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-white/10 gap-3">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-craft-amber-400 bg-craft-amber-400/10 px-2.5 py-1 rounded-full border border-craft-amber-400/30">
              Artisan Narrative Input
            </span>
            <h3 className="text-xl font-bold text-white font-serif-heading mt-2">
              Describe the Physical Process & Senses
            </h3>
          </div>
          <div className="text-xs text-stone-400 font-mono">
            {craftDescription.length} characters
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
          <div>
            <label className="block text-xs font-bold text-stone-300 mb-1.5 uppercase tracking-wide">
              Craft Tradition Name
            </label>
            <input
              type="text"
              value={craftName}
              onChange={(e) => setCraftName(e.target.value)}
              placeholder="e.g. Madurai Sungudi"
              className="w-full px-4 py-3 text-sm rounded-xl bg-black/40 border border-white/15 text-white placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-craft-amber-400/50"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-stone-300 mb-1.5 uppercase tracking-wide">
              Master Artisan Attribution
            </label>
            <input
              type="text"
              value={artisanName}
              onChange={(e) => setArtisanName(e.target.value)}
              placeholder="e.g. Meenakshi Ammal"
              className="w-full px-4 py-3 text-sm rounded-xl bg-black/40 border border-white/15 text-white placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-craft-amber-400/50"
            />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-xs font-bold text-stone-300 mb-1.5 uppercase tracking-wide">
            Detailed Demonstration Notes (Include feel, temperature, sound, and error warnings)
          </label>
          <textarea
            rows={7}
            value={craftDescription}
            onChange={(e) => setCraftDescription(e.target.value)}
            placeholder="Describe what you do, what materials you touch, the resistance in your fingertips, the heat of the bath..."
            className="w-full p-4 text-sm rounded-2xl bg-black/40 border border-white/15 text-stone-100 placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-craft-amber-400/50 font-sans leading-relaxed"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-white/10">
          <label className="flex items-center gap-2 text-xs text-stone-400 cursor-pointer">
            <input
              type="checkbox"
              checked={artisanApproved}
              onChange={(e) => setArtisanApproved(e.target.checked)}
              className="w-4 h-4 rounded text-craft-amber-400 focus:ring-craft-amber-400 bg-black/40 border-white/20"
            />
            <span>Artisan consent verified (GI Ethical Heritage Attribution)</span>
          </label>

          <button
            onClick={onGenerateQuestions}
            disabled={!craftDescription.trim() || isGeneratingQuestions}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 via-craft-amber-300 to-amber-200 hover:from-craft-amber-300 hover:to-amber-100 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl shadow-lg shadow-amber-900/30 transition-all cursor-pointer"
          >
            {isGeneratingQuestions ? (
              <>
                <Search className="w-4 h-4 animate-spin text-craft-indigo-950" />
                <span>Observer & Interviewer Agents Running...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4 text-craft-indigo-950" />
                <span>Analyze & Reveal Tacit Knowledge Gaps</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Observer Findings Display */}
      {observation && (
        <div className="hud-glass rounded-3xl p-6 sm:p-8">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-ping" />
              <h3 className="text-base font-bold uppercase tracking-wider text-white font-serif-heading">
                Observer Agent Analysis Findings
              </h3>
            </div>
            <span className="text-xs text-stone-400">
              Visible process extracted · Tacit gaps identified
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Steps */}
            <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-1.5 text-xs font-bold text-blue-300 mb-2.5">
                <Layers className="w-4 h-4" />
                Visible Steps ({observation.visible_steps?.length || 0})
              </div>
              <ul className="text-xs text-stone-300 space-y-2 list-disc pl-4 leading-relaxed">
                {observation.visible_steps?.slice(0, 4).map((s, idx) => (
                  <li key={idx} className="line-clamp-2">{s}</li>
                ))}
              </ul>
            </div>

            {/* Tools */}
            <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-300 mb-2.5">
                <Wrench className="w-4 h-4" />
                Tools Identified ({observation.tools_identified?.length || 0})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {observation.tools_identified?.map((t, idx) => (
                  <span
                    key={idx}
                    className="inline-block px-2.5 py-1 rounded-lg bg-white/10 text-[11px] text-stone-200 font-medium"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Materials */}
            <div className="p-4.5 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-1.5 text-xs font-bold text-purple-300 mb-2.5">
                <Package className="w-4 h-4" />
                Materials Identified ({observation.materials_identified?.length || 0})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {observation.materials_identified?.map((m, idx) => (
                  <span
                    key={idx}
                    className="inline-block px-2.5 py-1 rounded-lg bg-purple-950/40 text-purple-200 text-[11px] font-medium border border-purple-800/40"
                  >
                    {m}
                  </span>
                ))}
              </div>
            </div>

            {/* Gaps */}
            <div className="p-4.5 rounded-2xl bg-amber-500/10 border border-amber-400/40">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300 mb-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Tacit Knowledge Gaps ({observation.knowledge_gaps?.length || 0})
              </div>
              <ul className="text-xs text-amber-200 space-y-1.5 list-disc pl-4 leading-relaxed">
                {observation.knowledge_gaps?.slice(0, 4).map((g, idx) => (
                  <li key={idx} className="line-clamp-2">{g}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tacit Knowledge Interview Hub */}
      {questions.length > 0 && (
        <div className="hud-glass rounded-3xl p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-white/10 gap-3">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-purple-300 bg-purple-950/50 px-2.5 py-1 rounded-full border border-purple-800/40">
                Ethnographic Tacit Interview
              </span>
              <h3 className="text-xl font-bold text-white font-serif-heading mt-2">
                Probing the Hidden Touch ({answeredCount}/{questions.length} answered)
              </h3>
              <p className="text-xs text-stone-400 mt-0.5">
                Questions calibrated to extract muscle memory and sensory intuition.
              </p>
            </div>

            <button
              onClick={onFillSampleAnswers}
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold text-craft-amber-300 bg-craft-amber-400/15 hover:bg-craft-amber-400/25 rounded-xl border border-craft-amber-400/40 transition-colors cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-craft-amber-400" />
              Fill Master's Authentic Answers
            </button>
          </div>

          <div className="space-y-4 mb-8">
            {questions.map((q, idx) => {
              const isAnswered = Boolean(answers[q]?.trim());
              const isExpanded = activeQuestionIndex === idx;

              return (
                <div
                  key={idx}
                  className={`rounded-2xl border transition-all ${
                    isAnswered
                      ? 'border-emerald-500/40 bg-emerald-950/20'
                      : isExpanded
                      ? 'border-craft-amber-400/50 bg-white/10 shadow-lg'
                      : 'border-white/10 bg-black/30'
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => setActiveQuestionIndex(isExpanded ? null : idx)}
                    className="w-full p-4.5 flex items-start justify-between text-left gap-3 cursor-pointer"
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`w-7 h-7 rounded-xl text-xs font-bold flex items-center justify-center shrink-0 mt-0.5 ${
                          isAnswered
                            ? 'bg-emerald-500 text-black font-extrabold'
                            : 'bg-white/10 text-stone-300'
                        }`}
                      >
                        {idx + 1}
                      </span>
                      <div>
                        <p className="text-sm font-bold text-stone-100 leading-snug">
                          {q}
                        </p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-300 bg-purple-900/30 px-2 py-0.5 rounded border border-purple-700/40">
                            {idx === 0 || idx === 2
                              ? 'Tactile Resistance'
                              : idx === 1
                              ? 'Dye Saturation Cue'
                              : idx === 4
                              ? 'Error Recovery'
                              : 'Artisan Technique'}
                          </span>
                          {isAnswered && (
                            <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Answered
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <span className="text-stone-400 p-1">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </span>
                  </button>

                  {isExpanded && (
                    <div className="px-5 pb-5 pt-1 border-t border-white/10">
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-stone-400 mb-1.5">
                        Artisan's Response ({artisanName}):
                      </label>
                      <textarea
                        rows={3}
                        value={answers[q] || ''}
                        onChange={(e) => handleAnswerChange(q, e.target.value)}
                        placeholder="Type artisan explanation..."
                        className="w-full p-3.5 text-sm rounded-xl bg-black/40 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-craft-amber-400/50 leading-relaxed"
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Trigger Synthesis */}
          <div className="flex flex-col sm:flex-row items-center justify-between p-5 rounded-2xl bg-gradient-to-r from-purple-950 via-indigo-950 to-black border border-white/15 gap-4">
            <div>
              <h4 className="text-base font-bold font-serif-heading text-white">
                Ready to Crystallize the Skill DNA?
              </h4>
              <p className="text-xs text-stone-300 mt-0.5">
                The Knowledge Architect and Curriculum Agents will synthesize the structured fingerprint and masterclass.
              </p>
            </div>
            <button
              onClick={onCreateFingerprint}
              disabled={isCreatingFingerprint}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 via-craft-amber-300 to-amber-200 hover:from-craft-amber-300 hover:to-amber-100 disabled:opacity-40 rounded-xl shadow-lg transition-all cursor-pointer"
            >
              {isCreatingFingerprint ? (
                <>
                  <Building2 className="w-4 h-4 animate-spin text-craft-indigo-950" />
                  <span>Synthesizing Skill Fingerprint...</span>
                </>
              ) : (
                <>
                  <Building2 className="w-4 h-4 text-craft-indigo-950" />
                  <span>Synthesize Skill Fingerprint & Masterclass</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
