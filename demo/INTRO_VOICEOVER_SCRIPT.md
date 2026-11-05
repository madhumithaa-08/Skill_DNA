# SKILL DNA — 18-Second Intro Voiceover Script

Timed to `kit/results/intro.mp4` (18s @ 30fps, 1920×1080).
Record this as a single continuous take. Natural pace, documentary tone — not urgent, not slow.
Leave 0.5s silence at the start before speaking.

---

## [0:00 – 0:04]  The craft
*Screen: artisan hero image fades in, "The knowledge that lives in hands / deserves to live forever."*

> "For generations, traditional crafts have been passed from one pair of hands to another."

---

## [0:04 – 0:09]  The problem
*Screen: "What gets recorded? Steps. Instructions. Videos." / "What gets LOST? Experience. Judgment. Tacit knowledge."*

> "But the most valuable knowledge isn't always written down.
> It's the touch, the pressure, the timing — the decisions an artisan makes instinctively."

---

## [0:09 – 0:14]  The loss
*Screen: "When a master artisan retires… a piece of the craft retires with them. Permanently."*

> "When that knowledge isn't captured, every retiring artisan takes a piece of the craft with them."

**[Pause one beat after "with them." Let "Permanently." land in silence.]**

---

## [0:14 – 0:18]  SKILL DNA emerges
*Screen: Dark canvas. "SKILL DNA" title fades in amber. Pipeline diagram builds: ARTISAN KNOWLEDGE → OBSERVE → INTERVIEW → STRUCTURE → SKILL DNA*

> "SKILL DNA preserves the knowledge behind the craft."

**[Hard cut to website recording.]**

---

## Recording notes

- Total speaking time: ~16 seconds of speech across 18 seconds of video
- Tone: calm, intentional, documentary — like an opening to a short film, not a product ad
- The 1-second silence at the end of scene 3 ("Permanently.") is intentional — do not fill it
- Record at 48kHz / 24-bit if possible; 44.1kHz is fine
- Tools to merge voiceover + video: iMovie (drag audio track), DaVinci Resolve (free), or:
  ```bash
  ffmpeg -i kit/results/intro.mp4 -i your_voiceover.m4a \
    -c:v copy -c:a aac -shortest \
    kit/results/intro_with_audio.mp4
  ```

---

## Full submission video structure

```
intro_with_audio.mp4   (18s — this animation + your voiceover)
        +
demo.mp4               (134.6s — website recording)
        =
merge command:

ffmpeg -i intro_with_audio.mp4 -i kit/results/demo.mp4 \
  -filter_complex "[0:v][0:a][1:v]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  final_submission.mp4
```

Total: ~152s (~2:32) — well under the 3-minute limit.
