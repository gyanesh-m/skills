# Advanced Evaluation Patterns (TypeScript)

## Batch Evaluation Across Test Cases

```typescript
import { GalileoEvaluateWorkflow } from "@rungalileo/galileo";

const workflow = new GalileoEvaluateWorkflow("batch-eval");
await workflow.init();

const testCases = [
  { input: "What is ML?", context: "Machine learning is a subset of AI..." },
  { input: "Explain RAG", context: "Retrieval-augmented generation combines..." },
  { input: "What is fine-tuning?", context: "Fine-tuning adapts a pre-trained model..." },
];

for (const testCase of testCases) {
  workflow.addWorkflow({ input: testCase.input });

  workflow.addRetrieverStep({
    input: testCase.input,
    output: [testCase.context],
  });

  const response = await callYourLLM(testCase.input, testCase.context);

  workflow.addLlmStep({
    input: `Context: ${testCase.context}\nQuestion: ${testCase.input}`,
    output: response,
    durationNs: 1500000000,
    model: "gpt-4o",
  });

  workflow.concludeWorkflow(response);
}

await workflow.uploadWorkflows({
  context_adherence: true,
  chunk_attribution: true,
  completeness: true,
});
```

## Evaluating Multi-Step Agents

```typescript
const workflow = new GalileoEvaluateWorkflow("agent-eval");
await workflow.init();

workflow.addWorkflow({ input: "Research climate change impacts" });

workflow.addToolStep({
  input: "search: climate change impacts 2024",
  output: "Results: Rising temperatures, sea level rise...",
  durationNs: 300000000,
});

workflow.addRetrieverStep({
  input: "climate change impacts",
  output: [
    "Global temperatures have risen 1.1°C...",
    "Sea levels are projected to rise...",
  ],
});

workflow.addLlmStep({
  input: "Summarize the research on climate change impacts.",
  output: "Climate change is causing significant global impacts...",
  durationNs: 2000000000,
  model: "gpt-4o",
});

workflow.concludeWorkflow("Climate change is causing significant global impacts...");

await workflow.uploadWorkflows({
  context_adherence: true,
  completeness: true,
  toxicity: true,
});
```

## Comparing Models

Run the same test set across different models and compare results in the Galileo console:

```typescript
const models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"];

for (const model of models) {
  const workflow = new GalileoEvaluateWorkflow(`eval-${model}`);
  await workflow.init();

  for (const testCase of testCases) {
    workflow.addWorkflow({ input: testCase.input });
    const response = await callLLM(testCase.input, model);
    workflow.addLlmStep({
      input: testCase.input,
      output: response,
      durationNs: 1000000000,
      model,
    });
    workflow.concludeWorkflow(response);
  }

  await workflow.uploadWorkflows({
    correctness: true,
    completeness: true,
    uncertainty: true,
  });
}
```

## Best Practices

1. **Use descriptive project names** that include the experiment purpose and date.
2. **Include retriever steps** when evaluating RAG pipelines so context-dependent metrics are computed.
3. **Measure actual durations** using `performance.now()` or `Date.now()` converted to nanoseconds.
4. **Run evaluations in CI/CD** to catch quality regressions before deployment.
5. **Compare results in the Galileo console** to visualize metric trends across experiments.
