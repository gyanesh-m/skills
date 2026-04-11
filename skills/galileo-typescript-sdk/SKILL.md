---
name: galileo-typescript-sdk
description: Complete reference for the Galileo AI platform TypeScript/JS SDK for evaluating, observing, and protecting GenAI applications. Use when building Node.js or TypeScript applications that need LLM evaluation, production observability, tracing, or runtime guardrails with Galileo.
license: MIT
compatibility: Requires Node.js 18+. Works with npm, yarn, or pnpm.
metadata:
  author: gyanesh-m
  version: "1.0.0"
  sdk-version: "latest"
  sdk-repo: https://github.com/rungalileo/galileo-js
  docs: https://docs.galileo.ai
---

# Galileo TypeScript SDK

The Galileo TypeScript SDK (`@rungalileo/galileo`) provides evaluation and observability workflows for GenAI applications in Node.js and TypeScript. It supports logging LLM calls, retriever operations, tool invocations, and multi-step workflows with built-in scoring.

**Additional references:**

- [Framework Integrations](references/INTEGRATIONS.md) — Vercel AI SDK, Mastra, LangGraph (JS), and more
- [Guardrail Metrics Reference](references/METRICS.md) — Scoring metrics available for evaluation workflows
- [Advanced Evaluation Patterns](references/EVALUATION.md) — Complex workflow evaluation and experiment design

## Installation

```bash
npm install @rungalileo/galileo
```

Or with yarn/pnpm:

```bash
yarn add @rungalileo/galileo
pnpm add @rungalileo/galileo
```

## Quick Start

```typescript
import { GalileoObserveWorkflow } from "@rungalileo/galileo";

const workflow = new GalileoObserveWorkflow("my-observe-project");
await workflow.init();

workflow.addWorkflow({ input: "What is quantum computing?" });

workflow.addLlmStep({
  input: "What is quantum computing?",
  output: "Quantum computing uses quantum bits...",
  durationNs: 1500000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow("Quantum computing uses quantum bits...");

await workflow.uploadWorkflows();
```

## Authentication

Set the following environment variables in your `.env` file or shell:

```bash
GALILEO_API_KEY="your-api-key"            # Required — from Galileo console
GALILEO_CONSOLE_URL="https://app.galileo.ai"  # Console URL (or self-hosted)
```

Alternative authentication via username/password:

```bash
GALILEO_USERNAME="your-username"
GALILEO_PASSWORD="your-password"
```

## Observability with GalileoObserveWorkflow

### Basic Workflow Logging

```typescript
import { GalileoObserveWorkflow } from "@rungalileo/galileo";

const workflow = new GalileoObserveWorkflow("my-project");
await workflow.init();

workflow.addWorkflow({ input: "User question here" });

workflow.addLlmStep({
  input: "User question here",
  output: "LLM response text",
  durationNs: 1200000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow("LLM response text");

await workflow.uploadWorkflows();
```

### Logging Retriever Steps

```typescript
workflow.addWorkflow({ input: "What are the benefits of RAG?" });

workflow.addRetrieverStep({
  input: "What are the benefits of RAG?",
  output: ["Document 1 content", "Document 2 content"],
});

workflow.addLlmStep({
  input: "Based on the context, explain RAG benefits.",
  output: "RAG provides improved accuracy by...",
  durationNs: 2000000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow("RAG provides improved accuracy by...");
```

### Logging Tool Steps

```typescript
workflow.addWorkflow({ input: "Calculate 15 * 42" });

workflow.addToolStep({
  input: "15 * 42",
  output: "630",
  durationNs: 50000000,
});

workflow.addLlmStep({
  input: "The calculator returned 630. Respond to the user.",
  output: "15 multiplied by 42 equals 630.",
  durationNs: 800000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow("15 multiplied by 42 equals 630.");
```

## Evaluation with GalileoEvaluateWorkflow

### Running an Evaluation

```typescript
import { GalileoEvaluateWorkflow } from "@rungalileo/galileo";

const evaluateWorkflow = new GalileoEvaluateWorkflow("eval-project");
await evaluateWorkflow.init();

const testCases = [
  { input: "What is ML?", expected: "Machine learning is..." },
  { input: "Explain AI", expected: "Artificial intelligence is..." },
];

for (const testCase of testCases) {
  evaluateWorkflow.addWorkflow({ input: testCase.input });

  const response = await callYourLLM(testCase.input);

  evaluateWorkflow.addLlmStep({
    input: testCase.input,
    output: response,
    durationNs: 1000000000,
    model: "gpt-4o",
  });

  evaluateWorkflow.concludeWorkflow(response);
}

await evaluateWorkflow.uploadWorkflows({
  context_adherence: true,
  completeness: true,
  toxicity: true,
});
```

### Evaluation with RAG Steps

```typescript
const evaluateWorkflow = new GalileoEvaluateWorkflow("rag-eval");
await evaluateWorkflow.init();

evaluateWorkflow.addWorkflow({ input: "How does photosynthesis work?" });

evaluateWorkflow.addRetrieverStep({
  input: "How does photosynthesis work?",
  output: ["Photosynthesis is the process by which plants..."],
});

evaluateWorkflow.addLlmStep({
  input: "Using the context, explain photosynthesis.",
  output: "Photosynthesis is a process used by plants...",
  durationNs: 1500000000,
  model: "gpt-4o",
});

evaluateWorkflow.concludeWorkflow("Photosynthesis is a process used by plants...");

await evaluateWorkflow.uploadWorkflows({
  context_adherence: true,
  chunk_attribution: true,
});
```

## Common Patterns

### Multiple Workflows in a Single Upload

```typescript
const workflow = new GalileoObserveWorkflow("batch-project");
await workflow.init();

const queries = ["Question 1", "Question 2", "Question 3"];

for (const query of queries) {
  workflow.addWorkflow({ input: query });

  const response = await callYourLLM(query);

  workflow.addLlmStep({
    input: query,
    output: response,
    durationNs: 1000000000,
    model: "gpt-4o",
  });

  workflow.concludeWorkflow(response);
}

await workflow.uploadWorkflows();
```

### Nested Agent Workflows

```typescript
const workflow = new GalileoObserveWorkflow("agent-project");
await workflow.init();

workflow.addWorkflow({ input: "Research and summarize quantum computing" });

workflow.addToolStep({
  input: "search: quantum computing overview",
  output: "Search results...",
  durationNs: 200000000,
});

workflow.addRetrieverStep({
  input: "quantum computing",
  output: ["Doc1: Quantum bits...", "Doc2: Superposition..."],
});

workflow.addLlmStep({
  input: "Summarize the following research on quantum computing...",
  output: "Quantum computing leverages quantum mechanical phenomena...",
  durationNs: 2500000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow(
  "Quantum computing leverages quantum mechanical phenomena..."
);

await workflow.uploadWorkflows();
```

## Best Practices

1. **Always call `init()`** before adding workflows — it authenticates and sets up the project.
2. **Always call `concludeWorkflow()`** with the final output before starting the next workflow or uploading.
3. **Always call `uploadWorkflows()`** at the end to send data to Galileo.
4. **Use accurate `durationNs` values** — measure actual LLM call duration in nanoseconds for meaningful latency tracking.
5. **Set environment variables** in `.env` files rather than hardcoding API keys.
6. **Use `GalileoEvaluateWorkflow`** for test/eval runs and **`GalileoObserveWorkflow`** for production monitoring.
7. **Pass scorer configuration** to `uploadWorkflows()` in evaluate mode to get metric scores computed.

## Resources

- **Documentation:** https://docs.galileo.ai
- **TypeScript SDK repo:** https://github.com/rungalileo/galileo-js
- **SDK examples:** https://github.com/rungalileo/sdk-examples
- **npm:** https://www.npmjs.com/package/@rungalileo/galileo
- **Galileo console:** https://app.galileo.ai
