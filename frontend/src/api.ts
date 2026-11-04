import {
  ObservationData,
  SkillFingerprint,
  LessonModule,
  FingerprintSummary,
} from './types';

const API_BASE = '';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchSampleNotes(): Promise<{
  success: boolean;
  craft_name: string;
  artisan_name: string;
  notes: string;
}> {
  const res = await fetch(`${API_BASE}/api/sample-notes`);
  if (!res.ok) throw new Error('Failed to load sample notes');
  return res.json();
}

export async function fetchDemoData(): Promise<{
  success: boolean;
  is_demo: boolean;
  observation: ObservationData;
  questions: string[];
  fingerprint: SkillFingerprint;
  lesson: LessonModule;
}> {
  const res = await fetch(`${API_BASE}/api/demo/data`);
  if (!res.ok) throw new Error('Failed to load demo data');
  return res.json();
}

export async function runObserver(description: string, craftName: string, artisanName: string): Promise<{
  success: boolean;
  is_demo: boolean;
  observation: ObservationData;
}> {
  const res = await fetch(`${API_BASE}/api/pipeline/observe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      description,
      craft_name: craftName,
      artisan_name: artisanName,
    }),
  });
  if (!res.ok) throw new Error('Observer Agent request failed');
  return res.json();
}

export async function runInterviewer(knowledgeGaps: string[], craftName: string): Promise<{
  success: boolean;
  is_demo: boolean;
  questions: string[];
}> {
  const res = await fetch(`${API_BASE}/api/pipeline/interview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      knowledge_gaps: knowledgeGaps,
      craft_name: craftName,
    }),
  });
  if (!res.ok) throw new Error('Interviewer Agent request failed');
  return res.json();
}

export async function createFingerprintAndLesson(
  observation: ObservationData,
  answers: Record<string, string>,
  craftName: string,
  artisanName: string
): Promise<{
  success: boolean;
  is_demo: boolean;
  fingerprint: SkillFingerprint;
  lesson: LessonModule;
}> {
  const res = await fetch(`${API_BASE}/api/pipeline/fingerprint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      observation,
      answers,
      craft_name: craftName,
      artisan_name: artisanName,
    }),
  });
  if (!res.ok) throw new Error('Failed to synthesize fingerprint');
  return res.json();
}

export async function fetchFingerprintsList(): Promise<{
  success: boolean;
  fingerprints: FingerprintSummary[];
}> {
  const res = await fetch(`${API_BASE}/api/fingerprints`);
  if (!res.ok) throw new Error('Failed to fetch fingerprints list');
  return res.json();
}

export async function fetchFingerprintFile(filename: string): Promise<{
  success: boolean;
  fingerprint: SkillFingerprint;
}> {
  const res = await fetch(`${API_BASE}/api/fingerprints/${encodeURIComponent(filename)}`);
  if (!res.ok) throw new Error('Failed to load fingerprint file');
  return res.json();
}

export async function sendMentorMessage(learnerId: string, message: string): Promise<{
  success: boolean;
  is_demo: boolean;
  learner_id: string;
  response: string;
}> {
  const res = await fetch(`${API_BASE}/api/learner/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: learnerId, message }),
  });
  if (!res.ok) throw new Error('Failed to reach mentor agent');
  return res.json();
}


// ---------------------------------------------------------------------------
// Amazon Polly — lesson audio
// ---------------------------------------------------------------------------

export async function synthesizeSpeech(text: string, voiceId: string = 'Kajal'): Promise<{
  success: boolean;
  status: string;
  audio_url?: string;
  error?: string;
}> {
  const res = await fetch(`${API_BASE}/api/polly/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice_id: voiceId }),
  });
  if (!res.ok) throw new Error('Polly synthesis failed');
  return res.json();
}

export async function synthesizeLessonStep(step: object): Promise<{
  success: boolean;
  audio_url?: string;
  error?: string;
}> {
  const res = await fetch(`${API_BASE}/api/polly/lesson-step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(step),
  });
  if (!res.ok) throw new Error('Polly step synthesis failed');
  return res.json();
}

// ---------------------------------------------------------------------------
// Amazon Transcribe — artisan audio → text
// ---------------------------------------------------------------------------

export async function transcribeAudio(
  audioFile: File,
  language: string = 'en-IN',
  artisanName: string = 'artisan',
): Promise<{
  success: boolean;
  status: string;
  transcript?: string;
  job_name?: string;
  error?: string;
}> {
  const form = new FormData();
  form.append('audio', audioFile);
  form.append('language', language);
  form.append('artisan_name', artisanName);
  const res = await fetch(`${API_BASE}/api/transcribe/upload`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error('Transcription request failed');
  return res.json();
}

// ---------------------------------------------------------------------------
// DynamoDB — learner progress
// ---------------------------------------------------------------------------

export async function saveLearnerProgress(
  learnerId: string,
  craftName: string,
  quizScore: number,
  totalQuestions: number,
  completedSteps: number[],
): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/api/learner/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      learner_id: learnerId,
      craft_name: craftName,
      message: `Quiz completed: ${quizScore}/${totalQuestions}`,
      quiz_score: quizScore,
      total_questions: totalQuestions,
      completed_steps: completedSteps,
    }),
  });
  if (!res.ok) throw new Error('Failed to save progress');
  return res.json();
}

export async function getLearnerProgress(learnerId: string, craftName?: string): Promise<{
  success: boolean;
  progress: any;
}> {
  const url = craftName
    ? `${API_BASE}/api/learner/${encodeURIComponent(learnerId)}/progress?craft_name=${encodeURIComponent(craftName)}`
    : `${API_BASE}/api/learner/${encodeURIComponent(learnerId)}/progress`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load progress');
  return res.json();
}

// ---------------------------------------------------------------------------
// Health check with AWS services status (extended version)
// ---------------------------------------------------------------------------

export async function checkHealthFull(): Promise<{
  status: string;
  aws_services: Record<string, string>;
  version: string;
}> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}
