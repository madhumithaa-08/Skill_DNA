import React, { useState, useRef } from 'react';
import { Header } from './components/Header';
import { ArtisanHero } from './components/ArtisanHero';
import { PipelineVisualizer } from './components/PipelineVisualizer';
import { ArtisanStudio } from './components/ArtisanStudio';
import { SkillFingerprintView } from './components/SkillFingerprintView';
import { LearnerStudio } from './components/LearnerStudio';
import { SavedFingerprintsModal } from './components/SavedFingerprintsModal';
import {
  ObservationData,
  SkillFingerprint,
  LessonModule,
  PipelineStage,
  CraftPreset,
} from './types';
import {
  fetchSampleNotes,
  fetchDemoData,
  runObserver,
  runInterviewer,
  createFingerprintAndLesson,
} from './api';
import { ArrowLeft, ArrowRight, Dna } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'artisan' | 'fingerprint' | 'learner'>('artisan');
  const [currentStage, setCurrentStage] = useState<PipelineStage>('idle');
  const [activeStatusText, setActiveStatusText] = useState<string>('');
  const [activeCraftId, setActiveCraftId] = useState<string>('madurai-sungudi');

  // Artisan state
  const [craftName, setCraftName] = useState<string>('Madurai Sungudi');
  const [artisanName, setArtisanName] = useState<string>('Meenakshi Ammal');
  const [craftDescription, setCraftDescription] = useState<string>('');
  const [observation, setObservation] = useState<ObservationData | null>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  // Artifacts
  const [fingerprint, setFingerprint] = useState<SkillFingerprint | null>(null);
  const [lesson, setLesson] = useState<LessonModule | null>(null);

  // Loading states
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false);
  const [isCreatingFingerprint, setIsCreatingFingerprint] = useState(false);
  const [isDemoLoaded, setIsDemoLoaded] = useState(false);
  const [isLiveAI, setIsLiveAI] = useState(false);
  const [isArchivesOpen, setIsArchivesOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'info' | 'error' } | null>(null);
  const [pipelineSummary, setPipelineSummary] = useState<{
    stepsFound?: number;
    gapsFound?: number;
    questionsGenerated?: number;
    elapsedMs?: number;
  }>({});
  const pipelineStartRef = useRef<number>(0);

  const showToast = (text: string, type: 'success' | 'info' | 'error' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Select a preset craft from the hero
  const handleSelectCraft = (preset: CraftPreset) => {
    setActiveCraftId(preset.id);
    setCraftName(preset.craftName);
    setArtisanName(preset.artisanName);
    setCraftDescription(preset.description);
    showToast(`Loaded authentic notes for ${preset.artisanName} (${preset.craftName})!`, 'info');
    setActiveTab('artisan');
  };

  // 1-Click Load Full Demo
  const handleLoadDemo = async () => {
    try {
      setCurrentStage('observer');
      setActiveStatusText('Loading Madurai Sungudi demo...');
      const data = await fetchDemoData();

      setCraftName(data.fingerprint.craft_name);
      setArtisanName(data.fingerprint.artisan_name);
      setObservation(data.observation);
      setQuestions(data.questions);
      setFingerprint(data.fingerprint);
      setLesson(data.lesson);
      setIsDemoLoaded(true);
      setIsLiveAI(false);
      setCurrentStage('complete');
      setActiveStatusText('');

      showToast('Loaded Madurai Sungudi demo masterclass!', 'success');
      setActiveTab('fingerprint');
    } catch (err: any) {
      showToast(err.message || 'Failed to load demo data', 'error');
      setCurrentStage('idle');
      setActiveStatusText('');
    }
  };

  // Load sample Sungudi notes into text area
  const handleLoadSampleNotes = async () => {
    try {
      const data = await fetchSampleNotes();
      setCraftDescription(data.notes);
      setCraftName(data.craft_name);
      setArtisanName(data.artisan_name);
      setActiveCraftId('madurai-sungudi');
      showToast('Sample notes loaded: Meenakshi Ammal, 40-year Sungudi master', 'info');
    } catch (err: any) {
      showToast('Could not load notes file. Make sure API is running.', 'error');
    }
  };

  // Step 1: Observer & Interviewer Agents
  const handleGenerateQuestions = async () => {
    if (!craftDescription.trim()) return;

    setIsGeneratingQuestions(true);
    pipelineStartRef.current = Date.now();
    try {
      // Stage 1: Observer
      setCurrentStage('observer');
      setActiveStatusText('Observer Agent analyzing craft description for visible steps & tacit gaps...');
      const obsRes = await runObserver(craftDescription, craftName, artisanName);
      setObservation(obsRes.observation);
      if (!obsRes.is_demo) setIsLiveAI(true);

      const stepsCount = obsRes.observation.visible_steps?.length || 0;
      const gapsCount = obsRes.observation.knowledge_gaps?.length || 0;

      // Stage 2: Interviewer
      setCurrentStage('interviewer');
      setActiveStatusText('Interviewer Agent formulating targeted tacit knowledge questions...');
      const gaps = obsRes.observation.knowledge_gaps || [
        'Knot tension and muscle resistance',
        'Dye temperature feel and readiness',
        'Error recovery when dye bleeds',
      ];
      const intRes = await runInterviewer(gaps, craftName);
      setQuestions(intRes.questions);

      const elapsed = Date.now() - pipelineStartRef.current;
      setPipelineSummary({
        stepsFound: stepsCount,
        gapsFound: gapsCount,
        questionsGenerated: intRes.questions.length,
        elapsedMs: elapsed,
      });

      setCurrentStage('idle');
      setActiveStatusText('');
      showToast(
        `Generated ${intRes.questions.length} targeted questions to draw out tacit knowledge!`,
        'success'
      );
    } catch (err: any) {
      showToast(err.message || 'Failed to generate questions', 'error');
      setCurrentStage('idle');
      setActiveStatusText('');
    } finally {
      setIsGeneratingQuestions(false);
    }
  };

  // Fill realistic master answers for quick testing & demoing
  const handleFillSampleAnswers = () => {
    const sampleResponses: Record<string, string> = {
      [questions[0] || 'default_1']:
        'You can feel it in your thumb and forefinger — when the thread tension is right, there is a firm resistance, like the knot is pushing back against you. If it feels loose, it will leak dye. I always do a test pull before I move to the next mark.',
      [questions[1] || 'default_2']:
        'I press a corner of the submerged fabric against a dry white test cloth. If it transfers a rich crimson without watering down, it is ready. If pale, I give it five more minutes and test again.',
      [questions[2] || 'default_3']:
        'The damp silk should feel uniformly heavy and pliable, like cool water running through your fingers. If there are dry spots, it will absorb dye unevenly and ruin the geometry.',
      [questions[3] || 'default_4']:
        'For traditional Sungudi, 1.5 cm is the sacred distance. Tighter spacing creates fine floral fields; wider spacing creates bold temple borders.',
      [questions[4] || 'default_5']:
        'If the water turns cloudy or grey smudges appear instead of crisp white circles, the knot tension was uneven.',
      [questions[5] || 'default_6']:
        'It took ten years with my mother watching my fingers before the tension became muscle memory. You cannot count wraps with a clock; you feel it in your body.',
    };

    setAnswers(sampleResponses);
    showToast('Auto-filled master artisan answers for demonstration!', 'info');
  };

  // Step 2: Knowledge Architect & Curriculum Agents
  const handleCreateFingerprint = async () => {
    setIsCreatingFingerprint(true);
    try {
      // Stage 3: Knowledge Architect
      setCurrentStage('knowledge_architect');
      setActiveStatusText('Knowledge Architect synthesizing versioned Skill Fingerprint...');
      
      const res = await createFingerprintAndLesson(
        observation || {},
        answers,
        craftName,
        artisanName
      );

      // Stage 4: Curriculum
      setCurrentStage('curriculum');
      setActiveStatusText('Curriculum Agent structuring interactive learner masterclass...');

      setFingerprint(res.fingerprint);
      setLesson(res.lesson);

      setTimeout(() => {
        setCurrentStage('complete');
        setActiveStatusText('');
        showToast('🧬 Skill Fingerprint & Masterclass created successfully!', 'success');
        setActiveTab('fingerprint');
      }, 800);
    } catch (err: any) {
      showToast(err.message || 'Error creating fingerprint', 'error');
      setCurrentStage('idle');
      setActiveStatusText('');
    } finally {
      setIsCreatingFingerprint(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07060f] text-stone-100 flex flex-col font-sans celestial-bg relative">
      
      {/* Subtle Atmospheric Fixed Background Image */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden opacity-25">
        <img
          src="/artisan_hero.jpg"
          alt="Celestial artisan background"
          className="w-full h-full object-cover object-center filter blur-xs brightness-60 contrast-125"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#07060f] via-[#07060f]/80 to-transparent" />
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`fixed bottom-6 right-6 z-50 px-5 py-3.5 rounded-2xl shadow-2xl border text-xs sm:text-sm font-bold flex items-center gap-2.5 animate-in slide-in-from-bottom-5 ${
            toastMessage.type === 'success'
              ? 'bg-emerald-950 text-emerald-200 border-emerald-600 shadow-emerald-950/60'
              : toastMessage.type === 'error'
              ? 'bg-rose-950 text-rose-200 border-rose-600 shadow-rose-950/60'
              : 'bg-purple-950 text-amber-200 border-purple-600 shadow-purple-950/60'
          }`}
        >
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Floating Holographic Header */}
      <Header
        onLoadDemo={handleLoadDemo}
        onOpenArchives={() => setIsArchivesOpen(true)}
        isDemoLoaded={isDemoLoaded}
        hasFingerprint={Boolean(fingerprint)}
        isLiveAI={isLiveAI}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Celestial Content */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Full-Bleed Artisan Hero Stage */}
        <ArtisanHero
          onSelectCraft={handleSelectCraft}
          onExploreDemo={handleLoadDemo}
          activeCraftId={activeCraftId}
        />

        {/* Multi-Agent Pipeline Visualizer */}
        <PipelineVisualizer
          currentStage={currentStage}
          activeStatusText={activeStatusText}
          isDemo={!isLiveAI}
          pipelineSummary={pipelineSummary}
        />

        {/* Seamless Stage Content */}
        {activeTab === 'artisan' && (
          <div className="space-y-6">
            <ArtisanStudio
              craftName={craftName}
              setCraftName={setCraftName}
              artisanName={artisanName}
              setArtisanName={setArtisanName}
              craftDescription={craftDescription}
              setCraftDescription={setCraftDescription}
              onLoadSampleNotes={handleLoadSampleNotes}
              onGenerateQuestions={handleGenerateQuestions}
              isGeneratingQuestions={isGeneratingQuestions}
              observation={observation}
              questions={questions}
              answers={answers}
              setAnswers={setAnswers}
              onCreateFingerprint={handleCreateFingerprint}
              isCreatingFingerprint={isCreatingFingerprint}
              onFillSampleAnswers={handleFillSampleAnswers}
            />

            {/* Seamless Progression Pill */}
            {fingerprint && (
              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setActiveTab('fingerprint')}
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 text-craft-indigo-950 font-bold text-xs sm:text-sm shadow-lg hover:scale-102 transition-all cursor-pointer"
                >
                  <span>Advance to Stage 02: Skill DNA</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'fingerprint' && (
          <div className="space-y-6">
            <SkillFingerprintView
              fingerprint={fingerprint}
              onGoToLearner={() => setActiveTab('learner')}
            />

            {/* Seamless Cycle Controls */}
            <div className="flex items-center justify-between pt-4">
              <button
                onClick={() => setActiveTab('artisan')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-stone-300 text-xs sm:text-sm font-semibold transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Stage 01: Artisan Capture</span>
              </button>

              <button
                onClick={() => setActiveTab('learner')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 text-craft-indigo-950 font-bold text-xs sm:text-sm shadow-lg hover:scale-102 transition-all cursor-pointer"
              >
                <span>Advance to Stage 03: Masterclass</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {activeTab === 'learner' && (
          <div className="space-y-6">
            <LearnerStudio
              lesson={lesson}
              onLoadDemoLesson={handleLoadDemo}
              onGoToArtisan={() => setActiveTab('artisan')}
            />

            {/* Seamless Return Control */}
            <div className="flex justify-start pt-4">
              <button
                onClick={() => setActiveTab('fingerprint')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-stone-300 text-xs sm:text-sm font-semibold transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Return to Stage 02: Skill DNA</span>
              </button>
            </div>
          </div>
        )}

      </main>

      {/* Saved Fingerprints Archive Modal */}
      <SavedFingerprintsModal
        isOpen={isArchivesOpen}
        onClose={() => setIsArchivesOpen(false)}
        onSelectFingerprint={(savedFp) => {
          setFingerprint(savedFp);
          setActiveTab('fingerprint');
          showToast(`Loaded ${savedFp.craft_name} from archives!`, 'success');
        }}
      />

      {/* Celestial Footer */}
      <footer className="relative z-10 border-t border-white/10 bg-black/60 backdrop-blur-xl py-8 text-center text-xs text-stone-400 mt-16">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-stone-300">
            <Dna className="w-4 h-4 text-craft-amber-400" />
            <p className="font-semibold">
              SKILL DNA — Preserving Intangible Traditional Craft Knowledge
            </p>
          </div>
          <p className="italic text-stone-500">
            Dedicated with deep cultural reverence to Meenakshi Ammal and master artisans worldwide.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
