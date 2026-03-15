# Guardrail Metrics Reference (TypeScript)

Galileo provides built-in scoring metrics that can be enabled when uploading evaluation workflows. These metrics are computed server-side by the Galileo platform.

## Available Scorer Metrics

Pass these as configuration keys to `uploadWorkflows()` in `GalileoEvaluateWorkflow`:

| Metric Key | Description | Best For |
|---|---|---|
| `context_adherence` | Measures whether responses are grounded in provided context | RAG pipelines, context-based Q&A |
| `chunk_attribution` | Whether each retrieved chunk contributed to the response | RAG retrieval quality |
| `chunk_utilization` | How much of each retrieved chunk was used in generation | Optimizing chunk sizes |
| `completeness` | Whether the response fully addresses the input query | Q&A, customer support |
| `instruction_adherence` | Response alignment with system instructions | Instruction-following tasks |
| `uncertainty` | Model certainty level — correlates with hallucinations | Hallucination detection |
| `correctness` | Whether response facts are verifiable | Factual accuracy |
| `toxicity` | Detects abusive or toxic language | Content moderation |
| `pii` | Surfaces personally identifiable information | Privacy compliance |
| `prompt_injection` | Identifies adversarial prompt injection attempts | Security |
| `sexism` | Detects gender-biased content | Bias detection |
| `tone` | Classifies responses into emotion categories | Brand voice, CX |

## Usage in Evaluate Workflows

```typescript
import { GalileoEvaluateWorkflow } from "@rungalileo/galileo";

const workflow = new GalileoEvaluateWorkflow("eval-project");
await workflow.init();

// ... add workflows and steps ...

await workflow.uploadWorkflows({
  context_adherence: true,
  completeness: true,
  toxicity: true,
  pii: true,
  prompt_injection: true,
});
```

## Selecting Metrics by Use Case

**RAG applications:**
```typescript
await workflow.uploadWorkflows({
  context_adherence: true,
  chunk_attribution: true,
  chunk_utilization: true,
  completeness: true,
});
```

**Safety-critical applications:**
```typescript
await workflow.uploadWorkflows({
  toxicity: true,
  pii: true,
  prompt_injection: true,
  sexism: true,
});
```

**General quality assessment:**
```typescript
await workflow.uploadWorkflows({
  uncertainty: true,
  correctness: true,
  completeness: true,
  tone: true,
});
```
