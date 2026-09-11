# JP — Japanese Learning Project

지피티와 함께하는 언어 공부 일본어편. 
generated and assisted by GPT-6 Astra, GPT-5.6 Sol 

Personal Japanese-learning workspace focused on artificial immersion, literacy acquisition, productive Japanese, and eventual JLPT N1 proficiency.

## Goal

The primary objective is genuine advanced Japanese proficiency.

JLPT N1 is treated as an important benchmark, but not as the curriculum itself.

The intended progression is:

> existing spoken Japanese  
> → literacy unlock  
> → productive conversion  
> → formal-register expansion  
> → advanced native comprehension  
> → JLPT N1 optimization

---

## Learner Profile

The learner acquired much of their existing Japanese informally through anime, music, and repeated exposure.

Current ability is strongly asymmetric:

- listening/receptive Japanese is relatively strong
- conversational grammar often exists implicitly
- spontaneous production is weaker than comprehension
- kanji reading is a major bottleneck
- handwriting is minimal
- formal/written vocabulary is substantially weaker than everyday vocabulary

The canonical learner state is maintained in:

> `JAPANESE_PROFILE.md`

Read that file before beginning or continuing a lesson.

---

## Core Method

The project uses an artificial-immersion approach.

Preferred loop:

> meaningful input  
> → attempted interpretation  
> → spontaneous output  
> → minimal corrective recast  
> → contextual explanation  
> → delayed retrieval  
> → reuse in new contexts

Grammar is primarily used to organize and compress language already encountered rather than as the starting point of instruction.

---

## Kanji Strategy

Do not use isolated handwriting-heavy kanji study as the default.

Prefer lexical mappings such as:

> 判断 → はんだん → 판단  
> 状況 → じょうきょう → 상황  
> 影響 → えいきょう → 영향

For already-known spoken vocabulary:

> 怒る → おこる → known spoken concept

The main goal is:

> written form ↔ Japanese reading ↔ existing meaning

Priority:

> recognition > reading > IME production > handwriting

---

## Korean Advantage

Sino-Korean vocabulary should be used aggressively when the correspondence is valid.

However, semantic drift and false friends must be identified explicitly.

A Korean semantic inference does not automatically imply mastery of:

- Japanese reading
- Japanese collocation
- register
- productive usage

---

## Default Lesson Structure

A typical lesson contains four integrated components.

### 1. Reading Unlock

Read natural Japanese without automatic furigana.

Identify whether failures come from:

- unknown orthography
- unknown reading
- unknown vocabulary
- grammar
- reading-selection errors

### 2. Production

Produce Japanese from realistic situations.

Do not provide the target grammar construction beforehand.

### 3. Native Material

Use authentic Japanese from areas the learner genuinely cares about.

Possible material:

- anime
- songs
- YouTube
- games
- Japanese communities
- sports
- economics
- news
- essays
- interviews

### 4. Retrieval

Recycle previous errors in new contexts.

The learner should retrieve the target without explicit prompting.

---

## Review State

Vocabulary and grammar may move through:

> NEW  
> → LEARNING  
> → PARTIALLY_STABLE  
> → STABLE  
> → MASTERED

Items can be demoted after later failure.

Recognition and production should be tracked separately.

---

## Error Categories

Useful canonical labels:

- `SPOKEN_WORD_KNOWN_ORTHOGRAPHY_UNKNOWN`
- `MEANING_INFERRED_FROM_KOREAN`
- `WORD_UNKNOWN`
- `GRAMMAR_UNKNOWN`
- `GRAMMAR_RECEPTIVE_ONLY`
- `READING_SELECTION_ERROR`
- `CONTEXTUAL_INFERENCE_SUCCESS`

These distinctions are important because the learner's Japanese ability is highly asymmetric.

---

## Checkpoints

Run an unseen checkpoint approximately every 10 substantial lessons.

Assess separately:

1. kanji-word reading
2. vocabulary
3. conversational grammar
4. formal grammar
5. reading comprehension
6. spontaneous production
7. productive naturalness
8. listening when available

Do not evaluate progress only through JLPT-style questions.

---

## JLPT N1

N1-specific preparation should become intensive only after general literacy and reading fluency improve.

Later test preparation may include:

- N1 vocabulary
- N1 grammar
- paraphrase recognition
- long-form reading
- discourse analysis
- time management
- listening format
- mock tests

The project principle is:

> acquire Japanese first; optimize for the test second.

---

## Repository Workflow

`JAPANESE_PROFILE.md` is the canonical current-state file.

It should be updated when a lesson produces a meaningful change in:

- learner profile
- confirmed strengths
- recurring errors
- review state
- curriculum
- checkpoint results

Do not copy entire lesson transcripts into the profile.

If detailed lesson records are later desired, use a separate structure such as:

```text
JP/
├── README.md
├── JAPANESE_PROFILE.md
├── lessons/
│   ├── 001.md
│   ├── 002.md
│   └── ...
└── checkpoints/
    ├── checkpoint_001.md
    └── ...
```

The lesson files are optional.

The learner profile remains the source of truth for continuing instruction across separate ChatGPT sessions.


## Lesson Logs

Every substantial lesson should be preserved as a separate lesson log.

Directory structure:

```text
JP/
├── README.md
├── JAPANESE_PROFILE.md
├── lessons/
│   ├── 001.md
│   ├── 002.md
│   ├── 003.md
│   └── ...
└── checkpoints/
    ├── checkpoint_001.md
    └── ...
```

### Purpose

Lesson logs are the historical record of the learning process.

Unlike `JAPANESE_PROFILE.md`, which represents the learner's current state, lesson logs should preserve what actually happened during each lesson.

They are used to:

- preserve original learner responses
- preserve generated exercises and prompts
- distinguish genuine retrieval from previously exposed material
- analyze recurring errors
- compare old and new production
- reconstruct why an item entered the review queue
- evaluate long-term progress
- prevent future instructors from relying only on compressed profile summaries

---

### What to Record

Each lesson log should preserve, in chronological order:

1. lesson number and date
2. lesson objectives
3. exercises/questions generated by the instructor
4. the learner's original answers
5. instructor corrections
6. explanations that materially contributed to learning
7. important learner questions or observations
8. error classification
9. newly introduced vocabulary/grammar
10. retrieval results for previously learned items
11. end-of-lesson state changes

The learner's original answers should normally be preserved verbatim, including:

- incorrect readings
- uncertain guesses
- Korean phonetic transcriptions
- self-corrections
- reasoning comments
- explicit uncertainty such as `?`
- mixed Korean/Japanese answers

Do NOT silently clean up the learner's answer before recording it.

The original error pattern is useful learning data.

---

### Recommended Lesson File Format

```md
# Lesson 001

Date: YYYY-MM-DD

## Objectives

- ...
- ...

## Part A — Reading Unlock

### Question 1

> Japanese source sentence

### Learner Response

> Original learner response preserved verbatim.

### Review

- Correct reading:
- Meaning:
- Correction:
- Notes:

### Classification

- `SPOKEN_WORD_KNOWN_ORTHOGRAPHY_UNKNOWN`
- `READING_SELECTION_ERROR`

---

## Part B — Production

### Prompt

> Korean or situational production prompt

### Learner Response

> Original learner production

### Natural Japanese

> Corrected/natural version

### Review

Explanation of the important difference.

### Classification

- `GRAMMAR_RECEPTIVE_ONLY`

---

## Part C — Native Material

...

---

## Part D — Retrieval

...

---

## New Items

### Vocabulary

- ...

### Grammar

- ...

## Retrieval Results

- item → SUCCESS
- item → PARTIAL
- item → FAIL

## State Changes

- `～わけじゃない`: RECEPTIVE_NOT_PRODUCTIVE → LEARNING
- `判断`: NEW → LEARNING

## Instructor Summary

Brief description of what changed during this lesson and what the next lesson should target.
```

The exact format may vary when pedagogically useful, but the distinction between the original learner response and the corrected answer must remain clear.

---

### Verbatim Preservation Rule

When a lesson occurs in ChatGPT, preserve the learner's substantive exercise answers as written whenever practical.

For example, if the learner writes:

> 슈죠?(주장인데 발음이 애매해서 찍음)

do not replace the historical response with:

> しゅちょう

Instead record both:

```md
Learner:
> 슈죠?(주장인데 발음이 애매해서 찍음)

Correction:
> 主張（しゅちょう）
```

The learner's uncertainty and reasoning are part of the diagnostic evidence.

Casual conversation unrelated to the lesson does not need to be archived.

---

### Generated Exercise Preservation

Preserve the instructor's original exercise before the learner's answer.

This is necessary to distinguish:

- prompted knowledge
- contextual inference
- unprompted retrieval
- recognition after previous exposure

Do not rewrite an old exercise after seeing the learner's answer.

---

### Corrections

Preserve meaningful corrections and explanations.

Minor conversational filler does not need to be recorded.

If an instructor initially gives an incorrect explanation and later corrects it, the lesson log should make the correction explicit rather than silently rewriting history when the distinction matters educationally.

---

### State Update Rule

At the end of each substantial lesson:

1. create/update the corresponding `lessons/NNN.md`
2. identify actual learner-state changes
3. update `JAPANESE_PROFILE.md` only with those durable changes

Therefore:

> lesson log = historical evidence

while:

> learner profile = current best model

Do not copy the entire lesson log into `JAPANESE_PROFILE.md`.

---

### Cross-Session Continuity

When starting a new ChatGPT lesson session:

1. read `JAPANESE_PROFILE.md`
2. inspect the most recent lesson log when necessary
3. inspect older lesson logs only when needed for retrieval history or comparison
4. continue from the current learner state
5. avoid retesting recently exposed material as if it were unseen

For checkpoints, use genuinely unseen material whenever possible.

---

### Lesson Numbering

Use zero-padded sequential numbering:

```text
001.md
002.md
003.md
...
010.md
...
100.md
```

A single lesson may span multiple conversational turns.

Do not create a new lesson number merely because the ChatGPT session changed.

Conversely, if one ChatGPT conversation contains multiple clearly separate study sessions, they may be recorded as separate lessons.

The pedagogical session, not the ChatGPT thread, determines the lesson boundary.

