export interface Material {
  name: string;
  description: string;
  source: string;
}

export interface Technique {
  name: string;
  stage: string;
  description: string;
  duration_estimate: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tips: string[];
}

export interface Decision {
  decision_point: string;
  options: string[];
  artisan_choice: string;
  reasoning: string;
}

export interface CommonMistake {
  mistake: string;
  consequence: string;
  correction: string;
}

export interface MasteryRequirement {
  skill: string;
  how_to_demonstrate: string;
}

export interface SkillFingerprint {
  craft_name: string;
  craft_origin: string;
  craft_heritage: string;
  artisan_name: string;
  artisan_approved: boolean;
  cultural_significance: string;
  materials: Material[];
  techniques: Technique[];
  decisions: Decision[];
  common_mistakes: CommonMistake[];
  mastery_requirements: MasteryRequirement[];
  created_at: string;
  version: string;
}

export interface PracticeStep {
  step_number: number;
  instruction: string;
  what_to_watch_for: string;
  common_mistakes: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

export interface LessonModule {
  title: string;
  level: string;
  craft_name: string;
  overview: string;
  learning_objectives: string[];
  practice_steps: PracticeStep[];
  quiz: QuizQuestion[];
  estimated_duration_minutes: number;
}

export interface ObservationData {
  visible_steps?: string[];
  tools_identified?: string[];
  materials_identified?: string[];
  knowledge_gaps?: string[];
  [key: string]: any;
}

export type PipelineStage = 'idle' | 'observer' | 'interviewer' | 'knowledge_architect' | 'curriculum' | 'complete';

export interface FingerprintSummary {
  filename: string;
  path: string;
  craft_name: string;
  artisan_name: string;
  created_at: string;
  version: string;
  materials_count: number;
  techniques_count: number;
}

export interface CraftPreset {
  id: string;
  craftName: string;
  artisanName: string;
  origin: string;
  heritage: string;
  experienceYears: number;
  description: string;
  tagline: string;
  accentColor: string;
  avatarSeed: string;
}

export interface MentorChatMessage {
  id: string;
  sender: 'user' | 'mentor';
  text: string;
  timestamp: string;
}

