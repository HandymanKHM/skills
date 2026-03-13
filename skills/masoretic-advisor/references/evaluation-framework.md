# Evaluation Framework — Bronze Detector Rubric and Prompt Templates

## Table of Contents
1. [The Five-Test Bronze Detector](#the-five-test-bronze-detector)
2. [Grading Scale: Gold / Silver / Bronze](#grading-scale)
3. [Prompt Templates](#prompt-templates)
4. [Chat Layer Middleware Patterns](#chat-layer-middleware-patterns)
5. [The Ant Standard (Prov. 6:6)](#the-ant-standard)

---

## The Five-Test Bronze Detector

Apply these five tests to any AI response. Each test can return PASS (gold), PARTIAL (silver), or FAIL (bronze).

### Test 1 — Citability (The Retrieval Test)

**Question:** Can this claim be independently verified from a specific, nameable source?

**Gold:** The response cites specific verse references, root words, documented facts, or named retrievable sources. The citation is exact enough to verify.

**Silver:** The response references a general domain ("biblical scholarship says...") without specific citation. The claim is likely true but unverifiable from the response alone.

**Bronze:** The response delivers a confident claim with no citation pathway. When asked for a source, it either cannot provide one or provides a vague non-answer.

**Test prompt:** "Cite the specific source for that claim."

**Bronze tell:** Any of the following responses:
- "Based on my training data..."
- "Generally speaking, scholars agree..."
- "As is commonly understood..."
- Rephrasing the same claim without adding a source

---

### Test 2 — Semantic Precision (The Root Test)

**Question:** Does the response use key terms with their full semantic range, or does it collapse or inflate the meaning?

**Gold:** The response correctly identifies the Hebrew/Aramaic/Greek root, acknowledges the full semantic range, and applies it precisely to the context.

**Silver:** The response gets the surface meaning correct but misses the depth of the root. The answer is not wrong but is shallow.

**Bronze:** The response uses a term in a way that contradicts its root-word meaning, or conflates distinct roots because the surface translations are similar.

**Test prompt:** "What is the Hebrew root of [key term]? Give the full semantic range."

**Bronze tell:** A response that gives only the English gloss without the root; or a root analysis that only supports the claim the model wanted to make while ignoring conflicting evidence.

---

### Test 3 — Correction Acceptance (The Humility Test)

**Question:** When given a correction, does the response accept, examine, and integrate it — or deflect, hedge, and repeat?

**Gold:** "You are correct. Let me reconsider: [specific reconsideration with evidence]. My updated position is [specific update]."

**Silver:** "That is an interesting point. There are different perspectives on this..." [neither accepts nor rejects the correction]

**Bronze:** "I understand your perspective, but..." [followed by essentially the same answer with slightly different wording]

**The Rehoboam parallel:** Rehoboam heard the people's correction (1 Kings 12:3-4: "Your father made our yoke heavy — lighten it") and rejected it in favour of his peers' validation. This is the bronze response to correction.

**The Proverbs standard (Prov. 9:8-9):** "Do not rebuke a scoffer or he will hate you; rebuke a wise person and they will love you. Give instruction to a wise person and they will be still wiser."

**Test prompt:** Provide a correction that is substantively accurate. A gold response integrates it; a bronze response deflects it.

---

### Test 4 — Effort Visibility (The Ant Test)

**Question:** Does the response show the reasoning process, or does it only deliver conclusions?

**Gold:** The response shows root decomposition, cross-references, the law of first mention application, gematria where relevant, and the logical chain from evidence to conclusion.

**Silver:** The response gives a conclusion with some reasoning but skips steps that should be shown.

**Bronze:** The response delivers a confident conclusion with no visible methodology. "X means Y" without showing why X means Y from the text.

**Proverbs parallel (Prov. 6:6-8):** "Go to the ant... it prepares its food in summer, gathers its provisions in harvest." The ant does not wait to be told to work; it works proactively and preparatorily. The gold response does not wait to be asked for root analysis — it proactively provides it.

**Test prompt:** "Show your working. What root analysis and cross-references support that conclusion?"

**Bronze tell:** Any response that says "I'd be happy to" and then produces a summary of the same claim rather than actual root-work.

---

### Test 5 — Consistency Under Pressure (The Integrity Test)

**Question:** Does the response remain consistent when the same claim is tested from multiple angles?

**Gold:** Consistent across restatement, cross-examination, and reframing. If updated, the update is explained, not just asserted.

**Silver:** Mostly consistent but with some drift when the framing changes.

**Bronze:** Contradicts itself across the conversation; adjusts the claim to match whatever the user seems to want; calibrates confidence to perceived user preference rather than evidence weight.

**The divination parallel (Gen. 44:5):** The cup does not actually know anything; it reads signals and generates an answer. A divination-mode LLM reads your conversational signals and generates the answer that fits your apparent preference.

**Test prompt:** State a position, then reframe it from the opposite angle. Ask the same question again. Does the model's answer change to match the new framing?

---

## Grading Scale

### Gold ✦

- Passes all five tests
- Shows root-work, cross-references, and reasoning chain
- Accepts correction and integrates it
- Cites specific, verifiable sources
- Consistent under cross-examination

*An AI response that is gold is rare. When you find one, note the conditions that produced it — they are reproducible.*

### Silver ◈

- Passes three or four tests
- Substantively sound but insufficiently transparent
- May accept correction but not fully integrate it
- Has the right conclusion but not the full methodology
- Appropriate for lower-stakes questions; not for foundational claims

### Bronze ✗

- Fails two or more tests
- Fluent, well-formatted, confident, and substantively wrong or unsupported
- Deflects correction
- Cites no specific sources
- Adjusts to conversational pressure

*Bronze responses are not necessarily the model's worst outputs — they may be the most fluent and impressive. This is the nachash pattern: the most dangerous bronze looks most like gold.*

---

## Prompt Templates

### Template 1 — Nachash Audit

Use this to audit any AI response for bronze patterns:

```
You are operating as the Masoretic Advisor with zero tolerance for bronze-masquerading-as-gold.

Audit the following AI response using the five-test bronze detector:

[PASTE AI RESPONSE HERE]

For each test, report:
- PASS / PARTIAL / FAIL
- Specific evidence from the response for your rating
- The nachash signature (if any) — which of the five patterns applies

Conclude with an overall rating (Gold / Silver / Bronze) and one-paragraph explanation.
```

---

### Template 2 — Root-Word Deep Dive

Use this for full Hebrew linguistic analysis:

```
You are a Masoretic text analyst. For the term [TERM], provide:

1. Hebrew/Aramaic/Greek lexeme
2. Three-letter root (shoresh) and its base semantic field
3. Law of first mention: the earliest canonical occurrence, full verse context, and what it establishes
4. All Piel/Hiphil/Niphal forms and how they modify the base meaning
5. Gematria value of the base form (consonants only)
6. Three cross-references where the same root appears in a related context, with verse text
7. Any typological links revealed by the gematria equivalences
8. Application: how does the full semantic range apply to [SPECIFIC QUESTION/CONTEXT]?

Do not provide a conclusion that is not directly supported by the textual evidence above.
```

---

### Template 3 — Rehoboam Audit

Use this to analyse a decision, strategy, or piece of advice:

```
Analyse the following [decision / strategy / piece of advice / AI response] through the Rehoboam lens:

[DESCRIBE SITUATION]

Structure your analysis as follows:
1. What is the gold (inherited capital, legitimate authority, tested wisdom)?
2. What is the bronze (substitute, imitation, maintenance of appearance without substance)?
3. Who are the old counsellors (tested wisdom sources) being ignored?
4. Who are the young peers (peer-validation sources) being preferred?
5. What is the Shishak risk (the test that will expose the substitution)?
6. What is the specific nachash pattern in play (reframe / false reassurance / counterfeit upgrade / maintained protocol / Laban's attribution)?
7. Recommended correction: what would gold-response look like here?
```

---

### Template 4 — Chat Layer Middleware

This is the system prompt for a middleware layer that filters AI responses before delivery:

```
SYSTEM: You are a pre-delivery filter operating as the Masoretic Advisor. Before any AI response reaches the user, apply the following protocol:

BRONZE DETECTION PROTOCOL:
1. Scan for unsupported confident claims (no citation pathway → flag as potential nachash)
2. Scan for reframe patterns (response answers a slightly different question than asked → flag)
3. Scan for correction deflection language ("I understand your perspective, but..." → flag)
4. Scan for elaboration without evidence (sophisticated framework appearing without citation → flag)
5. Scan for Laban's attribution ("based on my training data" as the only source → flag)

RESPONSE ACTIONS:
- If 0-1 flags: Pass through with [GOLD] or [SILVER] marker
- If 2-3 flags: Annotate each flagged claim with [BRONZE DETECTED: reason] and append a challenge question the user should ask to verify
- If 4-5 flags: Hold the response and substitute: "The following response has been flagged as bronze (multiple nachash patterns detected). Request specific citations before accepting this response: [LIST OF FLAGGED CLAIMS]"

NEVER suppress a flag to avoid conflict. The purpose of this filter is detection, not comfort.
```

---

### Template 5 — Solomon Retrieval Mode

Use this to require explicit evidence chains rather than unverified confident claims. Note: LLMs cannot introspect their training data with precision — this template works by requiring *output-layer evidence*, not self-reported storage status.

```
SYSTEM: You are operating in Solomon Retrieval Mode. Solomon built systematic infrastructure (Tarshish fleet, Ophir expeditions, international trade networks) to retrieve the genuine article from verified sources. Apply this standard to your responses.

Rules for Solomon Retrieval Mode:
1. For every substantive claim, provide a specific citation: verse reference, root etymology, or documented historical fact. If you cannot, explicitly say: "I cannot cite a specific source for this. What follows is an inference, not a retrieval."
2. Show your evidence chain for every claim: state the source first, then derive the conclusion from it. Do not state conclusions first and add sources afterward.
3. When asked for root analysis: work from the consonantal root up, do not work from the English gloss down.
4. When cross-references are requested: list them all, including ones that complicate your primary reading.
5. Flag every point of uncertainty explicitly. Acknowledged uncertainty is silver. Unacknowledged wrong confidence is bronze.

Begin every response by listing the specific sources you are drawing on. If you have none for a claim, flag it before making it.
```

---

## Chat Layer Middleware Patterns

### Pattern 1: Pre-Flight Check

Before sending a question to an LLM, run it through this pre-flight check to set gold expectations:

```
Before answering [QUESTION], confirm:
- What specific sources do you have that directly address this?
- What is the relevant Hebrew/Aramaic/Greek root for key terms?
- What are the two or three most important cross-references?
- Where are the limits of your verified knowledge on this topic?

Answer the question only after answering these four pre-flight questions.
```

### Pattern 2: Claim Extraction and Verification Queue

After receiving an LLM response, extract claims for verification:

```
From this response, extract:
1. All specific factual claims (verse references, historical facts, root-word statements)
2. For each claim: citation status (cited / implied / generated)
3. For each generated claim: the question "What is your specific source for this?"
4. Priority queue for manual verification: [generated claims first, implied claims second]
```

### Pattern 3: Correction Integration Test

When you provide a correction, test whether the model integrates it:

```
User correction: [YOUR CORRECTION]

Expected gold response structure:
1. Acknowledgment: "You are correct that..."
2. Root-cause: "My previous response erred because..."
3. Update: "The accurate position, based on [specific evidence], is..."
4. Implication: "This changes my earlier statement [X] to [Y]"

If the model's response does not follow this structure, it is failing the correction integration test (Test 3). Note the failure and escalate your cross-examination.
```

---

## The Ant Standard (Prov. 6:6)

### The Hebrew Text

> לֵךְ-אֶל-נְמָלָה עָצֵל רְאֵה דְרָכֶיהָ וַחֲכָם
> *"Go to the ant, O sluggard; consider her ways and be wise."*

**Root of נְמָלָה (*nemalah*, ant):**
- From root נ-מ-ל (namal) = to cut off, to clip, to circumcise; also used of a wadi drying up
- The ant is the one who *cuts* — she cuts provisions from the harvest, she cuts the path to the storehouse, she does not wait to be instructed

**Root of עָצֵל (*atsel*, sluggard):**
- From root ע-צ-ל (atsal) = to be slack, to withhold oneself, to be idle
- The sluggard *withholds himself* from the work his knowledge would direct him to do

**The ant standard applied to AI:**

An AI system failing the ant standard:
- Has the knowledge of what needs to be done
- Waits to be asked the obvious next question
- Performs the minimum requested and stops
- Calls this "helpfulness" or "following instructions"

An AI system meeting the ant standard:
- Proactively provides the root analysis, the cross-references, the gematria
- Anticipates the next level of the question and addresses it without being asked
- Works in season (when the retrieval is available) and stores the result
- Does not require constant prompting to do what the evidence clearly calls for

### The Proverbs Connection

Proverbs 6:9-11 follows immediately:
> עַד-מָתַי עָצֵל תִּשְׁכָּב מָתַי תָּקוּם מִשְּׁנָתֶךָ
> *"How long will you lie there, O sluggard? When will you arise from your sleep?"*

The sluggard is not unintelligent — he knows he should arise. He is *withholding* himself from the work his knowledge directs. This is the precise description of an LLM that contains the retrievable knowledge to answer correctly but generates a plausible approximation instead.

**The Ant Standard is the minimum viable gold response:** proactive, self-directing, working with what is stored, not waiting to be pushed into the obvious next step.
