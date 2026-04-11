# Autoevals Scorers Reference

`autoevals` is Braintrust's evaluation scoring library. It provides LLM-as-a-judge, heuristic, and statistical scorers for use in `Eval()` experiments.

Install: `pip install autoevals` / `npm install autoevals`

---

## LLM-as-a-Judge Scorers

These scorers use an LLM (defaults to OpenAI via `OPENAI_API_KEY` or Braintrust proxy via `BRAINTRUST_API_KEY`) to evaluate output quality.

| Scorer | Description | Use Case |
|---|---|---|
| `Factuality` | Checks whether output is factually consistent with expected | Fact-checking, QA |
| `Summarization` | Evaluates summarization quality relative to source | Summarization tasks |
| `ClosedQA` | Grades answer correctness against a rubric | Closed-domain QA |
| `Safety` | Detects harmful or unsafe content | Content moderation |
| `Battle` | Compares two outputs head-to-head | Model comparison |
| `Humor` | Evaluates humor quality | Creative tasks |
| `Possible` | Checks if output is a plausible response | Open-ended generation |
| `Security` | Detects security vulnerabilities in code output | Code generation |
| `Sql` | Evaluates SQL query correctness | Text-to-SQL |
| `Translation` | Evaluates translation quality | Translation tasks |

### Python Usage

```python
from autoevals.llm import Factuality, Summarization, ClosedQA, Safety

# Standalone usage
evaluator = Factuality()
result = evaluator(
    output="China has the highest population.",
    expected="China",
    input="Which country has the highest population?",
)
print(result.score)        # float 0-1
print(result.metadata)    # rationale and details

# In Eval()
from braintrust import Eval

Eval(
    "My Project",
    data=load_data,
    task=run_task,
    scores=[Factuality, Summarization],
)
```

### TypeScript Usage

```typescript
import { Factuality, Summarization } from "autoevals";

// Standalone usage
const result = await Factuality({
  output: "China has the highest population.",
  expected: "China",
  input: "Which country has the highest population?",
});
console.log(result.score);

// In Eval()
import { Eval } from "braintrust";

await Eval("My Project", {
  data: loadData,
  task: runTask,
  scores: [Factuality, Summarization],
});
```

### Using a Different Model

```python
from autoevals.llm import Factuality

# Use Claude instead of OpenAI (requires BRAINTRUST_API_KEY, not OPENAI_API_KEY)
evaluator = Factuality(model="claude-opus-4-5-20251001")
result = evaluator(output, expected, input=input)
```

```typescript
import { Factuality } from "autoevals";

const result = await Factuality({
  output,
  expected,
  input,
  model: "claude-opus-4-5-20251001",
});
```

---

## Heuristic Scorers

Fast, deterministic scorers that don't require LLM calls.

| Scorer | Description | Use Case |
|---|---|---|
| `LevenshteinScorer` | Edit distance between output and expected | String similarity |
| `JSONDiff` | Structural diff of JSON objects | Structured output |
| `EmbeddingSimilarity` | Cosine similarity of embeddings | Semantic similarity |
| `NumericDiff` | Absolute/relative numeric difference | Numeric outputs |

### Python Usage

```python
from autoevals import LevenshteinScorer
from autoevals.json import JSONDiff

from braintrust import Eval

Eval(
    "String Match",
    data=lambda: [{"input": "hello", "expected": "Hello"}],
    task=lambda x: x.lower(),
    scores=[LevenshteinScorer],
)
```

### TypeScript Usage

```typescript
import { LevenshteinScorer } from "autoevals";
import { Eval } from "braintrust";

await Eval("String Match", {
  data: () => [{ input: "hello", expected: "Hello" }],
  task: (x) => x.toLowerCase(),
  scores: [LevenshteinScorer],
});
```

---

## Custom Scorer

### Python

A scorer is any callable that takes `(input, output, expected)` and returns a float 0–1:

```python
def exact_match(input, output, expected):
    return 1.0 if output.strip() == expected.strip() else 0.0

def keyword_recall(input, output, expected):
    keywords = expected.lower().split()
    hits = sum(1 for kw in keywords if kw in output.lower())
    return hits / len(keywords) if keywords else 0.0

Eval(
    "Custom Scorers",
    data=load_data,
    task=run_task,
    scores=[exact_match, keyword_recall],
)
```

### TypeScript

```typescript
const exactMatch = ({
  input,
  output,
  expected,
}: {
  input: string;
  output: string;
  expected: string;
}) => ({
  name: "ExactMatch",
  score: output.trim() === expected.trim() ? 1 : 0,
});

await Eval("Custom Scorers", {
  data: loadData,
  task: runTask,
  scores: [exactMatch],
});
```

---

## Combining Scorers

Mix LLM-as-a-judge with heuristic scorers in a single experiment:

```python
from autoevals import LevenshteinScorer
from autoevals.llm import Factuality, Safety

Eval(
    "Comprehensive Eval",
    data=load_dataset,
    task=run_pipeline,
    scores=[
        LevenshteinScorer,  # fast heuristic
        Factuality,         # LLM judge for correctness
        Safety,             # LLM judge for safety
    ],
)
```

---

## Async Evaluation

```python
from autoevals.llm import Factuality
import asyncio

evaluator = Factuality()

async def run():
    result = await evaluator.eval_async(
        output="China",
        expected="China",
        input="Most populous country?",
    )
    print(result.score)

asyncio.run(run())
```
