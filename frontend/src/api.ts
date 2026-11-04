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

