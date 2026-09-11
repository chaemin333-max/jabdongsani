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
