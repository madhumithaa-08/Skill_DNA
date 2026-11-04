import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import {
  BookOpen,
  Clock,
  Award,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  RotateCcw,
  Check,
  Eye,
  Bot,
  User,
  Send,
  Loader2,
} from 'lucide-react';
import { LessonModule, MentorChatMessage } from '../types';
import { sendMentorMessage } from '../api';

interface LearnerStudioProps {
  lesson: LessonModule | null;
  onLoadDemoLesson: () => void;
  onGoToArtisan: () => void;
}

export const LearnerStudio: React.FC<LearnerStudioProps> = ({
  lesson,
  onLoadDemoLesson,
  onGoToArtisan,
}) => {
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [completedObjectives, setCompletedObjectives] = useState<number[]>([]);

  // Quiz state
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [isQuizSubmitted, setIsQuizSubmitted] = useState(false);

  // Mentor Chat state
  const [learnerId] = useState(() => `learner-${Math.random().toString(36).substring(2, 7)}`);
  const [chatMessages, setChatMessages] = useState<MentorChatMessage[]>([
    {
      id: 'welcome',
      sender: 'mentor',
      text: 'Namaste! I am your SKILL DNA Mentor Agent. As you practice tying your Sungudi knots and taking the quiz, ask me anything about touch, tension, or recovery.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  if (!lesson) {
    return (
      <div className="max-w-3xl mx-auto py-16 px-6 text-center hud-glass rounded-3xl">
        <div className="w-16 h-16 rounded-2xl bg-amber-400/10 text-craft-amber-400 mx-auto flex items-center justify-center mb-4 border border-craft-amber-400/30">
          <BookOpen className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white font-serif-heading mb-2">
          Learner Studio — The Apprentice Masterclass
        </h2>
        <p className="text-stone-400 text-sm max-w-md mx-auto mb-6 leading-relaxed">
          No active lesson loaded yet. Synthesize a craft in Stage 01, or load the pre-built Madurai Sungudi masterclass demo.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={onLoadDemoLesson}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 shadow-md transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-craft-indigo-950" />
            ▶ Load Demo Masterclass
          </button>
          <button
            onClick={onGoToArtisan}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-stone-300 bg-white/10 hover:bg-white/15 border border-white/10 transition-all cursor-pointer"
          >
            Go to Stage 01: Artisan Capture
          </button>
        </div>
      </div>
    );
  }

  const toggleObjective = (idx: number) => {
    setCompletedObjectives((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]
    );
  };

  const toggleStepCompleted = (idx: number) => {
    setCompletedSteps((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]
    );
  };

  const handleSelectAnswer = (qIndex: number, option: string) => {
    if (isQuizSubmitted) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [qIndex]: option,
    }));
  };

  const handleCheckQuiz = () => {
    setIsQuizSubmitted(true);
    let correctCount = 0;
    lesson.quiz.forEach((q, idx) => {
      if (selectedAnswers[idx] === q.correct_answer) {
        correctCount++;
      }
    });

    if (correctCount === lesson.quiz.length) {
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 },
      });
    }

    sendMentorMessage(
      learnerId,
      `I just scored ${correctCount}/${lesson.quiz.length} on the ${lesson.craft_name} quiz.`
    ).then((res) => {
      setChatMessages((prev) => [
        ...prev,
        {
          id: String(Date.now()),
          sender: 'mentor',
          text: res.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }).catch(() => {});
  };

  const handleResetQuiz = () => {
    setSelectedAnswers({});
    setIsQuizSubmitted(false);
  };

  const quizScore = lesson.quiz.reduce((score, q, idx) => {
    return selectedAnswers[idx] === q.correct_answer ? score + 1 : score;
  }, 0);

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isSendingMessage) return;

    const userMsg: MentorChatMessage = {
      id: String(Date.now()),
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsSendingMessage(true);

    try {
      const res = await sendMentorMessage(learnerId, text);
      const mentorMsg: MentorChatMessage = {
        id: String(Date.now() + 1),
        sender: 'mentor',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages((prev) => [...prev, mentorMsg]);
    } catch (err: any) {
      const errMsg: MentorChatMessage = {
        id: String(Date.now() + 1),
        sender: 'mentor',
        text: `Keep practising! The tension in your fingertips develops after hundreds of repetitions. Remember: 3 wraps firm, double knot.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      
      {/* Masterclass Banner */}
      <div className="hud-glass-amber rounded-3xl p-6 sm:p-8 text-white">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-craft-amber-400 text-craft-indigo-950">
            {lesson.craft_name} Masterclass
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-stone-200">
            Level: {lesson.level.toUpperCase()}
          </span>
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-stone-200">
            <Clock className="w-3.5 h-3.5 text-craft-amber-400" />
            ~{lesson.estimated_duration_minutes} minutes
          </span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-bold font-serif-heading text-white mb-3">
          {lesson.title}
        </h1>

        <p className="text-stone-300 text-xs sm:text-sm lg:text-base leading-relaxed max-w-3xl font-sans">
          {lesson.overview}
        </p>
      </div>

      {/* Learning Objectives Checklist */}
      <div className="hud-glass rounded-3xl p-6 sm:p-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base sm:text-lg font-bold text-white font-serif-heading flex items-center gap-2">
            <Award className="w-5 h-5 text-craft-amber-400" />
            Learning Objectives ({completedObjectives.length}/{lesson.learning_objectives.length} Mastered)
          </h2>
          <span className="text-xs text-stone-400">Click to stamp as mastered</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {lesson.learning_objectives.map((obj, idx) => {
            const isChecked = completedObjectives.includes(idx);
            return (
              <button
                key={idx}
                type="button"
                onClick={() => toggleObjective(idx)}
                className={`p-4 rounded-2xl border text-left flex items-start gap-3 transition-all cursor-pointer ${
                  isChecked
                    ? 'border-emerald-500/40 bg-emerald-950/30 text-white'
                    : 'border-white/10 bg-white/5 hover:bg-white/8 text-stone-300'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-lg flex items-center justify-center shrink-0 mt-0.5 border transition-all ${
                    isChecked
                      ? 'bg-emerald-500 border-emerald-400 text-black font-extrabold'
                      : 'border-white/20 bg-black/40'
                  }`}
                >
                  {isChecked && <Check className="w-3.5 h-3.5 stroke-3" />}
                </div>
                <span className="text-xs sm:text-sm leading-relaxed font-medium">{obj}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Hands-on Practice Steps */}
      <div className="hud-glass rounded-3xl p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-white/10 gap-4">
          <div>
            <h2 className="text-xl font-bold text-white font-serif-heading flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-craft-amber-400" />
              Tactile Practice Steps
            </h2>
            <p className="text-xs text-stone-400 mt-0.5">
              Sensory guidance calibrated to the artisan's tactile touch.
            </p>
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto">
            {lesson.practice_steps.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setActiveStepIndex(idx)}
                className={`w-9 h-9 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeStepIndex === idx
                    ? 'bg-craft-amber-400 text-craft-indigo-950 shadow-lg'
                    : completedSteps.includes(idx)
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-white/5 text-stone-400 hover:bg-white/10'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </div>

        {lesson.practice_steps[activeStepIndex] && (
          <div className="space-y-6">
            <div className="p-6 sm:p-8 rounded-3xl bg-white/5 border border-white/10">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-craft-amber-300 bg-craft-amber-400/15 px-3 py-1 rounded-full border border-craft-amber-400/30">
                  Step {activeStepIndex + 1} of {lesson.practice_steps.length}
                </span>
                <button
                  onClick={() => toggleStepCompleted(activeStepIndex)}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    completedSteps.includes(activeStepIndex)
                      ? 'bg-emerald-500 text-black border-emerald-400 font-extrabold'
                      : 'bg-white/10 text-stone-300 border-white/15 hover:bg-white/15'
                  }`}
                >
                  <Check className="w-3.5 h-3.5" />
                  {completedSteps.includes(activeStepIndex) ? 'Practice Stamped' : 'Mark as Practiced'}
                </button>
              </div>

              <h3 className="text-base sm:text-xl font-bold text-white mb-4 font-serif-heading leading-relaxed">
                {lesson.practice_steps[activeStepIndex].instruction}
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
                <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-400/30">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300 mb-2">
                    <Eye className="w-4 h-4 text-craft-amber-400" />
                    👁️ What to Feel & Watch For (Tactile Checkpoint):
                  </div>
                  <p className="text-xs sm:text-sm text-stone-200 leading-relaxed font-sans">
                    {lesson.practice_steps[activeStepIndex].what_to_watch_for}
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-rose-950/20 border border-rose-800/40">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-rose-300 mb-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    ⚠️ Common Pitfall & Mistake:
                  </div>
                  <p className="text-xs sm:text-sm text-stone-200 leading-relaxed font-sans">
                    {lesson.practice_steps[activeStepIndex].common_mistakes}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                disabled={activeStepIndex === 0}
                onClick={() => setActiveStepIndex((prev) => prev - 1)}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-bold text-stone-300 bg-white/10 hover:bg-white/15 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl transition-all cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous Step
              </button>

              <button
                disabled={activeStepIndex === lesson.practice_steps.length - 1}
                onClick={() => setActiveStepIndex((prev) => prev + 1)}
                className="inline-flex items-center gap-1.5 px-6 py-2.5 text-xs font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl shadow-md transition-all cursor-pointer"
              >
                Next Step
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Knowledge Quiz */}
      <div className="hud-glass rounded-3xl p-6 sm:p-8">
        <div className="pb-4 mb-6 border-b border-white/10">
          <span className="text-xs font-bold uppercase tracking-wider text-rose-300 bg-rose-950/50 px-2.5 py-1 rounded-full border border-rose-800/40">
            Apprentice Examination
          </span>
          <h2 className="text-xl font-bold text-white mt-2 font-serif-heading">
            Tacit Knowledge Quiz (5 Questions)
          </h2>
          <p className="text-xs text-stone-400 mt-0.5">
            Tests conceptual understanding of knot resistance, moisture balance, and GI tradition.
          </p>
        </div>

        <div className="space-y-6">
          {lesson.quiz.map((q, qIdx) => {
            const userAnswer = selectedAnswers[qIdx];
            const isCorrect = isQuizSubmitted && userAnswer === q.correct_answer;

            return (
              <div
                key={qIdx}
                className={`p-6 rounded-2xl border transition-all ${
                  isQuizSubmitted
                    ? isCorrect
                      ? 'border-emerald-500/40 bg-emerald-950/20'
                      : 'border-rose-500/40 bg-rose-950/20'
                    : 'border-white/10 bg-white/5'
                }`}
              >
                <div className="flex items-start gap-3 mb-4">
                  <span className="w-7 h-7 rounded-xl bg-white/10 text-craft-amber-300 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {qIdx + 1}
                  </span>
                  <h4 className="text-sm sm:text-base font-bold text-white font-serif-heading leading-snug">
                    {q.question}
                  </h4>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pl-10">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = userAnswer === opt;
                    const isOptionCorrect = opt === q.correct_answer;

                    let btnStyle = 'border-white/10 bg-black/40 hover:bg-white/10 text-stone-200';

                    if (isQuizSubmitted) {
                      if (isOptionCorrect) {
                        btnStyle = 'border-emerald-500 bg-emerald-950/50 text-emerald-200 font-bold ring-2 ring-emerald-500/40';
                      } else if (isSelected && !isOptionCorrect) {
                        btnStyle = 'border-rose-500 bg-rose-950/50 text-rose-300 font-bold line-through';
                      } else {
                        btnStyle = 'border-white/5 bg-black/20 opacity-30';
                      }
                    } else if (isSelected) {
                      btnStyle = 'border-craft-amber-400 bg-craft-amber-400/20 text-craft-amber-200 font-bold ring-2 ring-craft-amber-400/30';
                    }

                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => handleSelectAnswer(qIdx, opt)}
                        className={`p-3.5 text-xs sm:text-sm text-left rounded-xl border transition-all cursor-pointer ${btnStyle}`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>

                {isQuizSubmitted && (
                  <div className="mt-4 ml-10 p-4 rounded-xl bg-black/40 border border-white/10 text-xs text-stone-200 leading-relaxed">
                    <strong className="text-craft-amber-300 block mb-1">
                      💡 Master Artisan Explanation:
                    </strong>
                    {q.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Quiz Actions */}
        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          {isQuizSubmitted ? (
            <div className="flex items-center gap-3">
              <div className="text-sm font-bold text-white">
                Score: <span className="text-craft-amber-300 font-serif-heading text-xl">{quizScore} / {lesson.quiz.length}</span>
              </div>
              <span
                className={`text-xs px-3 py-1 rounded-full font-bold ${
                  quizScore === lesson.quiz.length
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : quizScore >= 3
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                }`}
              >
                {quizScore === lesson.quiz.length
                  ? '🌟 Perfect Score! You understand the master\'s touch!'
                  : quizScore >= 3
                  ? '👍 Good intuition! Review the moisture & wrap rules.'
                  : '📖 Review the practice steps and retake.'}
              </span>
            </div>
          ) : (
            <div className="text-xs text-stone-400">
              Answer all 5 questions to assess your craft understanding.
            </div>
          )}

          <div className="flex items-center gap-2">
            {isQuizSubmitted ? (
              <button
                onClick={handleResetQuiz}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-bold text-stone-300 bg-white/10 hover:bg-white/15 rounded-xl transition-all cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Retake Quiz
              </button>
            ) : (
              <button
                onClick={handleCheckQuiz}
                disabled={Object.keys(selectedAnswers).length === 0}
                className="inline-flex items-center gap-2 px-7 py-3 text-xs font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 disabled:opacity-40 rounded-xl shadow-md transition-all cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4 text-craft-indigo-950" />
                Check Answers
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Strands AI Artisan Mentor Live Chat Console */}
      <div className="hud-glass-amber rounded-3xl p-6 sm:p-8 text-white">
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-craft-amber-400 to-craft-crimson-600 flex items-center justify-center text-craft-indigo-950 shadow-md">
              <Bot className="w-5 h-5 text-craft-indigo-950" />
            </div>
            <div>
              <h3 className="text-base font-bold font-serif-heading text-white flex items-center gap-2">
                Strands AI Artisan Mentor
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  Session Memory Active
                </span>
              </h3>
              <p className="text-xs text-stone-400">
                Remembers your quiz scores, questions, and practice history across sessions (Learner ID: {learnerId})
              </p>
            </div>
          </div>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            'My knots leak dye, how do I fix the tension?',
            'How do I test dye temperature without a thermometer?',
            'What is the sacred meaning of the Sungudi red border?',
          ].map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(prompt)}
              className="px-3 py-1.5 rounded-xl text-xs bg-white/10 hover:bg-white/15 text-stone-200 border border-white/10 transition-colors text-left cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Chat Stream */}
        <div className="space-y-3 max-h-72 overflow-y-auto p-4 rounded-2xl bg-black/50 border border-white/10 mb-4 font-sans">
          {chatMessages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'mentor' && (
                <div className="w-7 h-7 rounded-lg bg-craft-amber-500 text-craft-indigo-950 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                  🧬
                </div>
              )}
              <div
                className={`max-w-[85%] sm:max-w-[75%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-craft-amber-400 text-craft-indigo-950 font-bold rounded-tr-none'
                    : 'bg-white/10 text-stone-100 rounded-tl-none border border-white/10'
                }`}
              >
                {msg.text}
                <div className={`text-[10px] mt-1 ${msg.sender === 'user' ? 'text-craft-indigo-950/70' : 'text-stone-400'}`}>
                  {msg.timestamp}
                </div>
              </div>
              {msg.sender === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-white/20 text-white flex items-center justify-center shrink-0 mt-0.5 text-xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isSendingMessage && (
            <div className="flex items-center gap-2 text-xs text-craft-amber-300 italic p-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-craft-amber-400" />
              Mentor recalling your craft journey...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask your mentor about knot tension, dye bath timing, or cultural meaning..."
            className="flex-1 px-4 py-3 rounded-xl bg-black/40 border border-white/15 text-white placeholder-stone-500 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-craft-amber-400/50"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || isSendingMessage}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 text-craft-indigo-950 font-bold text-xs sm:text-sm disabled:opacity-40 transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </div>

    </div>
  );
};
