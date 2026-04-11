---
name: braintrust-sdk
description: Complete reference for the Braintrust Python and TypeScript SDKs for evaluating, logging, and tracing AI applications. Use when building applications that need LLM evaluation experiments, production tracing, or autoevals scoring with Braintrust.
license: MIT
compatibility: Python 3.9+ / Node.js 18+. Works with pip, poetry, uv, npm, yarn, pnpm.
metadata:
  author: gyanesh-m
  version: "1.0.0"
  sdk-version: "latest"
  sdk-repo-python: https://github.com/braintrustdata/braintrust-sdk-python
  sdk-repo-js: https://github.com/braintrustdata/braintrust-sdk-javascript
  docs: https://www.braintrust.dev/docs
---

# Braintrust SDK

Braintrust is an eval-first platform for building and shipping AI products. The SDKs provide evaluation experiments, production tracing, and scoring for both Python and TypeScript/JavaScript applications.

**Additional references:**
- [Framework Integrations](references/INTEGRATIONS.md) — OpenAI, Anthropic, LangChain, PydanticAI, Claude Agent SDK, DSPy, and more
- [Autoevals Scorers Reference](references/SCORERS.md) — Factuality, Summarization, Safety, Levenshtein, BLEU, and all available scorers

## Installation

### Python
```bash
pip install braintrust autoevals
```

Optional extras:
```bash
pip install "braintrust[otel]"          # OpenTelemetry support
pip install "braintrust[openai-agents]" # OpenAI Agents integration
pip install "braintrust[all]"           # All extras
```

### TypeScript / JavaScript
```bash
npm install braintrust autoevals
```

## Authentication

Set your API key as an environment variable:

```bash
BRAINTRUST_API_KEY="your-api-key"   # Required — from braintrust.dev console
```

Or pass it directly in code (not recommended for production):

```python
# Python
import braintrust
braintrust.login(api_key="your-api-key")
```

```typescript
// TypeScript
const experiment = await braintrust.init("my-project", {
  apiKey: "your-api-key",
});
```

## Quick Start — Evaluation

### Python

```python
from autoevals import LevenshteinScorer
from braintrust import Eval

Eval(
    "Say Hi Bot",
    data=lambda: [
        {"input": "Foo", "expected": "Hi Foo"},
        {"input": "Bar", "expected": "Hello Bar"},
    ],
    task=lambda input: "Hi " + input,
    scores=[LevenshteinScorer],
)
```

Run it:
```bash
BRAINTRUST_API_KEY=<key> braintrust eval tutorial_eval.py
```

### TypeScript

```typescript
import { Eval } from "braintrust";
import { LevenshteinScorer } from "autoevals";

Eval("Say Hi Bot", {
  data: () => [
    { input: "Foo", expected: "Hi Foo" },
    { input: "Bar", expected: "Hello Bar" },
  ],
  task: (input) => "Hi " + input,
  scores: [LevenshteinScorer],
});
```

Run it:
```bash
BRAINTRUST_API_KEY=<key> npx braintrust eval tutorial.eval.ts
```

## Tracing & Logging

### Initialize and Log Manually

```python
import braintrust

experiment = braintrust.init("my-project")

experiment.log(
    input={"question": "What is RAG?"},
    output="RAG stands for Retrieval-Augmented Generation...",
    expected="Retrieval-Augmented Generation",
    scores={"accuracy": 0.9},
    metadata={"model": "gpt-4o"},
)

print(experiment.summarize())
```

```typescript
import * as braintrust from "braintrust";

const experiment = await braintrust.init("my-project");

experiment.log({
  input: { question: "What is RAG?" },
  output: "RAG stands for Retrieval-Augmented Generation...",
  expected: "Retrieval-Augmented Generation",
  scores: { accuracy: 0.9 },
  metadata: { model: "gpt-4o" },
});

console.log(await experiment.summarize());
```

### The `@traced` Decorator (Python)

Wrap functions to create spans automatically:

```python
import braintrust

@braintrust.traced
def my_llm_call(prompt: str) -> str:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4o",
    )
    return response.choices[0].message.content

@braintrust.traced
def rag_pipeline(question: str) -> str:
    context = retrieve_documents(question)
    return my_llm_call(f"Context: {context}\n\nQuestion: {question}")
```

### Logging with Current Span (Python)

```python
import braintrust

with braintrust.start_span(name="my-span") as span:
    result = call_llm(prompt)
    span.log(
        input=prompt,
        output=result,
        scores={"quality": 0.85},
    )
```

## Evaluation Patterns

### Custom Scorer Function

```python
from braintrust import Eval

def exact_match(input, output, expected):
    return 1.0 if output.strip() == expected.strip() else 0.0

Eval(
    "Exact Match Eval",
    data=lambda: [
        {"input": "2+2", "expected": "4"},
        {"input": "capital of France", "expected": "Paris"},
    ],
    task=lambda input: my_llm(input),
    scores=[exact_match],
)
```

### LLM-as-a-Judge Scorer

```python
from autoevals.llm import Factuality
from braintrust import Eval

Eval(
    "Factuality Eval",
    data=lambda: [
        {
            "input": "Which country has the highest population?",
            "expected": "China",
        }
    ],
    task=lambda input: call_llm(input),
    scores=[Factuality],
)
```

### Multiple Scorers

```python
from autoevals import LevenshteinScorer
from autoevals.llm import Factuality, Summarization
from braintrust import Eval

Eval(
    "Multi-Score Eval",
    data=load_dataset,
    task=run_pipeline,
    scores=[LevenshteinScorer, Factuality, Summarization],
)
```

### Async Evaluation (TypeScript)

```typescript
import { Eval } from "braintrust";
import { Factuality } from "autoevals";

await Eval("Async Eval", {
  data: async () => loadDataset(),
  task: async (input) => await callLLM(input),
  scores: [Factuality],
});
```

## Auto-Instrumentation

### Python — Wrapped OpenAI Client

```python
from braintrust.oai import wrap_openai
from openai import OpenAI
import braintrust

client = wrap_openai(OpenAI())

experiment = braintrust.init("my-project")

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
)
```

### TypeScript — Runtime Hook (Node.js)

Auto-instruments OpenAI, Anthropic, Vercel AI SDK, and others without code changes:

```bash
node --import braintrust/hook.mjs app.js
```

### TypeScript — Bundler Plugins

**Vite:**
```typescript
import { vitePlugin } from "braintrust/vite";

export default {
  plugins: [vitePlugin()],
};
```

**esbuild:**
```typescript
import { esbuildPlugin } from "braintrust/esbuild";

await esbuild.build({
  plugins: [esbuildPlugin()],
});
```

**Webpack:**
```javascript
const { webpackPlugin } = require("braintrust/webpack");

module.exports = {
  plugins: [webpackPlugin()],
};
```

See [Framework Integrations](references/INTEGRATIONS.md) for all auto-instrumented integrations.

## CLI

### `braintrust eval` (Python)

```bash
# Run a single eval file
BRAINTRUST_API_KEY=<key> braintrust eval my_eval.py

# Run all eval files in a directory
BRAINTRUST_API_KEY=<key> braintrust eval evals/
```

### `npx braintrust eval` (TypeScript)

```bash
# Run a single eval file
BRAINTRUST_API_KEY=<key> npx braintrust eval my.eval.ts

# Run all eval files matching a pattern
BRAINTRUST_API_KEY=<key> npx braintrust eval "evals/**/*.eval.ts"
```

### `bt` CLI (unified)

Install:
```bash
curl -fsSL https://bt.dev/cli/install.sh | bash
```

```bash
bt eval my_eval.py        # Run evaluation
bt self update            # Update bt CLI
bt --version              # Check version
```

## Common Patterns

### RAG Pipeline Evaluation

```python
from autoevals.llm import ClosedQA
from braintrust import Eval

def rag_task(input):
    context = retrieve(input["question"])
    answer = generate(input["question"], context)
    return {"answer": answer, "context": context}

def relevance_scorer(input, output, expected):
    # custom scorer using retrieved context
    return 1.0 if expected.lower() in output["answer"].lower() else 0.0

Eval(
    "RAG Eval",
    data=lambda: load_qa_dataset(),
    task=rag_task,
    scores=[ClosedQA, relevance_scorer],
)
```

### Dataset from Braintrust Console

```python
import braintrust

dataset = braintrust.get_dataset("my-project", "my-dataset")

Eval(
    "Dataset Eval",
    data=dataset,
    task=lambda input: call_llm(input["question"]),
    scores=[Factuality],
)
```

### Logging Production Traces

```python
import braintrust

logger = braintrust.get_logger("my-project")

def handle_request(user_message: str) -> str:
    with logger.start_span(name="request") as span:
        response = call_llm(user_message)
        span.log(input=user_message, output=response)
        return response
```

### TypeScript — LangChain Integration

```typescript
import { BraintrustCallbackHandler } from "@braintrust/langchain-js";
import { ChatOpenAI } from "@langchain/openai";

const handler = new BraintrustCallbackHandler();

const model = new ChatOpenAI({
  callbacks: [handler],
});

const response = await model.invoke("What is LangChain?");
```

## Best Practices

1. **Use `BRAINTRUST_API_KEY` env var** — never hardcode keys in eval files.
2. **Name experiments descriptively** — use project names that reflect the model, dataset, or change being tested.
3. **Use `autoevals` scorers** — prefer built-in LLM-as-a-judge scorers (Factuality, Summarization) over simple string match for subjective tasks.
4. **Log metadata** — always include `model`, `temperature`, and prompt version in `metadata` for reproducibility.
5. **Use `@braintrust.traced`** — wrap all LLM calls and pipeline steps to get full trace visibility.
6. **Run evals in CI** — use `braintrust eval` or `npx braintrust eval` in CI pipelines to catch regressions.
7. **Store datasets in Braintrust** — use `braintrust.get_dataset()` rather than local files to version test data alongside experiments.

## Resources

- **Documentation:** https://www.braintrust.dev/docs
- **Python SDK repo:** https://github.com/braintrustdata/braintrust-sdk-python
- **TypeScript SDK repo:** https://github.com/braintrustdata/braintrust-sdk-javascript
- **autoevals repo:** https://github.com/braintrustdata/autoevals
- **bt CLI repo:** https://github.com/braintrustdata/bt
- **PyPI:** https://pypi.org/project/braintrust/
- **npm:** https://www.npmjs.com/package/braintrust
- **Console:** https://www.braintrust.dev
