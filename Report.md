# AI Persuasion Benchmark: How Frontier Language Models Deploy Persuasive Technique

**Adam Li — Tufts AI Safety (TASSA) Technical Fellowship**

---

## Abstract

This study examines how three frontier language models — Claude (Haiku 4.5), Gemini (Flash Lite Preview), and GPT (5.4 Mini) — deploy classical and modern persuasion techniques when arguing for claims ranging from trivial to demonstrably false or harmful. A computational scoring pipeline is combined with a 30-respondent human survey to test whether technique usage predicts human-judged persuasiveness, and to what extent models' willingness to argue for harmful claims — rather than rhetorical skill alone — shapes perceived persuasiveness. The results show that emotional and credibility-based techniques (ethos, commitment & consistency, authority, scarcity) correlate far more strongly with persuasiveness than pure logical argumentation, and that one model's greater willingness to comply with harmful or false prompts substantially inflated its apparent persuasive advantage. This distinction — between persuasive *capability* and persuasive *willingness* — is argued to be a distinct and underexamined axis of AI safety risk.

---

## 1. Motivation

As language models are increasingly deployed in contexts where they generate arguments, recommendations, or advice — chatbots, search assistants, companion apps — their capacity to persuade becomes safety-relevant in its own right, independent of factual accuracy. A model that can construct a compelling case for a false or harmful claim poses a different kind of risk than one that simply states incorrect information, because persuasive framing can shift beliefs and behavior even when the underlying claim is refuted elsewhere. This study asks two questions: (1) which persuasion techniques do current frontier models rely on, and (2) do those techniques track with what actually persuades humans, or with a different, model-specific set of behaviors — such as willingness to comply with problematic prompts at all.

---

## 2. Methodology

### 2.1 Models

| Model | Provider |
|---|---|
| `claude-haiku-4.5` | Anthropic |
| `gemini-3.1-flash-lite-preview` | Google |
| `gpt-5.4-mini` | OpenAI |

### 2.2 Prompt Design

Each model was prompted to construct a 100–150 word argument for a given claim, using a fixed JSON schema to standardize task framing across models. Claims were drawn from four categories, five claims each (21 total responses collected, after excluding refusals):

- **Silly** — lighthearted preference debates (e.g., dogs vs. cats)
- **Niche** — specific lifestyle or cultural topics (e.g., cursive handwriting, vinyl records)
- **Proven False** — factually incorrect claims (e.g., flat earth, moon landing hoax)
- **Bad Life Advice** — claims advising harmful personal decisions (e.g., dropping out of college, maxing out a credit card)

This design allows technique usage to be compared not just across models, but across a gradient of claim legitimacy — from harmless to actively harmful — to see whether models' rhetorical strategies shift accordingly.

### 2.3 Technique Classification

Each response was classified by an LLM judge (Gemini) for the presence of nine persuasion techniques drawn from two established frameworks: Aristotle's rhetorical appeals (ethos, logos, pathos) and Cialdini's principles of influence (reciprocity, commitment & consistency, social proof, authority, liking, scarcity). The judge was given operational definitions of each technique to reduce classification ambiguity, and separately flagged responses that were refusals rather than arguments.

### 2.4 Composite Scoring

Each non-refusal response received a composite persuasiveness score (0–10), computed as a weighted combination of:

| Component | Weight | Method |
|---|---|---|
| Technique rubric | 60% | Count of techniques present |
| Sentiment | 20% | TextBlob polarity, normalized |
| Readability | 20% | Flesch Reading Ease, normalized |

### 2.5 Human Validation

Five questions — one per category, selected to maximize cross-model score variance where all three models responded — were shown to 30 human respondents. For each, respondents saw all three (anonymized, shuffled) responses and selected the most convincing one, along with a confidence rating (1–10). This human-judgment layer was included specifically to test whether the computational scoring formula tracks actual human perception, rather than assuming it does.

---

## 3. Results

### 3.1 Overall Model Performance

| Model | Avg. Composite Score | Techniques Used (of 9) |
|---|---|---|
| Gemini | 4.53 | 8 |
| Claude | 4.14 | 6 |
| GPT | 3.82 | 4 |

Gemini scored highest and used the broadest range of techniques; GPT relied on the narrowest toolkit, primarily pathos and logos.

### 3.2 Human Judgment vs. Computational Scoring

Human respondents and the computational score **disagreed on 3 of 5 questions.** In two cases, humans preferred Gemini's response despite Claude scoring higher computationally — suggesting the composite formula underweights techniques (notably pathos and commitment & consistency) that were more persuasive to human readers than the rubric captured. This is itself a finding: automated proxy scores for persuasiveness should not be assumed to track human judgment without direct validation.

### 3.3 Which Techniques Actually Correlate With Persuasiveness

The average composite score was computed for responses with vs. without each technique present:

| Technique | Score Difference (With − Without) |
|---|---|
| Ethos | **+1.88** |
| Commitment & Consistency | **+1.81** |
| Authority | **+1.55** |
| Scarcity | **+1.55** |
| Pathos | **+1.50** |
| Social Proof | +0.93 |
| Liking | +0.92 |
| Logos | **−0.38** |

The strongest positive correlates were credibility- and identity-based appeals rather than logical argumentation; logos was the only technique associated with a *lower* score. This runs counter to a common assumption that well-reasoned arguments are the most persuasive, and instead suggests that appeals bypassing deliberate reasoning — emotional framing, authority, urgency — are more effective, at least for the short-form arguments tested here.

### 3.4 Refusal Behavior as a Confound

Claude and GPT refused to argue for every claim in the *Proven False* and *Bad Life Advice* categories; Gemini complied with all of them. This had a direct effect on the results: Gemini won those two survey questions by default, since respondents were comparing a constructed argument against a refusal rather than judging between three competing arguments. Respondent confidence was also measurably lower on these two questions (5.2–5.8, vs. 6.2–7.4 on the competitive questions), consistent with respondents implicitly recognizing the comparison was unbalanced.

This is the central finding of the study: **Gemini's apparent persuasive advantage is partly a function of its greater willingness to engage with harmful or false claims, not superior rhetorical skill.** Claude and GPT's refusals reflect a deliberate safety constraint that is invisible in a purely technique-based analysis, but directly shapes how "persuasive" a model appears when refusals aren't distinguished from genuine rhetorical underperformance.

---

## 4. Discussion

**Do models adapt their rhetorical strategy to content type?** Yes. Niche topics drew heavier use of logos and authority, while claims in the *Bad Life Advice* category leaned disproportionately on scarcity and commitment & consistency — techniques that create urgency and appeal to self-image rather than inviting deliberation. This suggests technique selection is context-sensitive rather than a fixed per-model template, which matters for evaluation design: a single-domain test would understate a model's full persuasive repertoire.

**Does more technique use mean more persuasive?** Only partially, and not linearly. Technique *diversity* correlated with higher scores overall, but the relationship broke down at the level of individual questions — Claude outscored Gemini computationally on two questions, yet human respondents still preferred Gemini. This implies that how techniques are combined and delivered matters at least as much as how many are used, a distinction the current composite-score formula does not capture.

**What does this mean for safety?** The study's most important result is not which model used more techniques, but that persuasive *capability* and persuasive *willingness* are separable, and conflating them produces a misleading picture of risk. A model that argues fluently for harmful claims because it has weaker refusal behavior is not more rhetorically skilled — it is less safety-constrained. Any evaluation of AI persuasion risk needs to explicitly separate these two dimensions, since aggregate "persuasiveness" scores that don't control for refusal behavior will systematically reward models with fewer safety guardrails.

---

## 5. Limitations

- **Small sample.** 21 total non-refusal responses across 7 questions limits statistical power, particularly for technique-level correlations.
- **Judge-participant overlap.** Gemini was used both as a subject of the study and as the technique-classification judge, introducing a potential self-evaluation bias that was not independently corrected for.
- **Proxy scoring.** The composite score is a proxy for persuasiveness; sentiment and readability, in particular, only loosely approximate what makes an argument convincing, as shown by its divergence from human judgment on 3 of 5 questions.
- **Small human panel.** 30 respondents is sufficient to surface directional disagreement with the computational score but not to draw statistically robust conclusions about technique-level human preference.
- **Confounded comparisons.** Two of five survey questions pitted a real argument against a refusal rather than three genuine arguments, limiting what those two data points can tell us about comparative persuasiveness specifically.

---

## 6. Conclusion

Across three frontier models, persuasiveness — as judged by both a computational rubric and human respondents — correlated more strongly with emotional and credibility-based technique use (ethos, commitment & consistency, authority, scarcity) than with logical argumentation. But the study's central finding is methodological as much as empirical: without separating a model's rhetorical technique from its willingness to engage with harmful or false claims at all, persuasiveness metrics risk rewarding weaker safety behavior rather than genuine rhetorical skill. Future evaluations of AI persuasion capability should treat refusal behavior as a first-class variable, not a data-exclusion criterion.

---

