"""
agents — Strands Agent implementations for the SKILL DNA pipeline.

Pipeline order:
    1. ObserverAgent       — extracts visible process knowledge
    2. InterviewerAgent    — generates targeted tacit-knowledge questions
    3. KnowledgeArchitectAgent — builds the structured Skill Fingerprint
    4. CurriculumAgent     — generates learner lesson modules
    5. Orchestrator        — run_skill_capture_pipeline() coordinates all four
"""
