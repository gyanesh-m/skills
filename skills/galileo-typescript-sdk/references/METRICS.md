# Guardrail Metrics Reference (TypeScript)

Galileo provides built-in scoring metrics that can be used with `runExperiment` or `GalileoLogger`. These metrics are computed server-side by the Galileo platform.

## Available Scorer Metrics

Pass these as string keys to the `metrics` array in `runExperiment`:

| Metric Key | Description | Best For |
|---|---|---|
| `context_adherence` | Measures whether responses are grounded in provided context | RAG pipelines, context-based Q&A |
| `chunk_attribution_utilization` | Whether retrieved chunks contributed to and were used in the response | RAG retrieval quality |
| `completeness` | Whether the response fully addresses the input query | Q&A, customer support |
| `instruction_adherence` | Response alignment with system instructions | Instruction-following tasks |
| `context_relevance` | Relevance of retrieved context to the query | RAG retrieval tuning |
| `ground_truth_adherence` | Response alignment with ground truth | Accuracy benchmarking |
| `uncertainty` | Model certainty level — correlates with hallucinations | Hallucination detection |
| `correctness` | Whether response facts are verifiable | Factual accuracy |
| `input_toxicity` / `output_toxicity` | Detects abusive or toxic language | Content moderation |
| `input_pii` / `output_pii` | Surfaces personally identifiable information | Privacy compliance |
| `prompt_injection` | Identifies adversarial prompt injection attempts | Security |
| `input_sexist` / `output_sexist` | Detects gender-biased content | Bias detection |
| `input_tone` / `output_tone` | Classifies into emotion categories | Brand voice, CX |
| `agent_efficiency` | Measures agent task completion efficiency | Agentic workflows |
| `tool_selection_quality` | Quality of tool selection decisions | Agentic workflows |
| `tool_error_rate` | Rate of tool execution errors | Agentic workflows |

Many metrics also have `_luna` variants (e.g., `context_adherence_luna`) that use Galileo's small language model for faster, lower-cost scoring.

## Usage in Experiments

```typescript
import { runExperiment } from "galileo";

const result = await runExperiment({
  name: "safety-eval",
  datasetName: "my-test-dataset",
  metrics: ["context_adherence", "completeness", "input_toxicity", "input_pii", "prompt_injection"],
  projectName: "eval-project",
  function: async (input) => {
    return await callYourLLM(input.question);
  },
});
```

## Selecting Metrics by Use Case

**RAG applications:**
```typescript
metrics: ["context_adherence", "chunk_attribution_utilization", "completeness", "context_relevance"]
```

**Safety-critical applications:**
```typescript
metrics: ["input_toxicity", "output_toxicity", "input_pii", "output_pii", "prompt_injection", "input_sexist"]
```

**General quality assessment:**
```typescript
metrics: ["uncertainty", "correctness", "completeness", "input_tone"]
```

**Agentic workflows:**
```typescript
metrics: ["agent_efficiency", "tool_selection_quality", "tool_error_rate"]
```
