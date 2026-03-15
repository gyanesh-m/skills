# Advanced Evaluation Patterns

Galileo Evaluate enables running experiments on prompts, models, RAG pipelines, and agents using built-in and custom metrics.

## Prompt Experimentation

Run experiments with different prompt templates, models, and parameters:

```python
import promptquality as pq

pq.login("https://app.galileo.ai")

template = "You are an expert on {{domain}}. Answer: {{question}}"
data = {
    "domain": ["physics", "biology", "history"],
    "question": [
        "What is entropy?",
        "How does photosynthesis work?",
        "What caused the fall of Rome?",
    ],
}

pq.run(
    project_name="prompt-experiment",
    template=template,
    dataset=data,
    settings=pq.Settings(
        model_alias="ChatGPT (16K context)",
        temperature=0.7,
        max_tokens=500,
    ),
)
```

## Comparing Model Configurations

Run the same evaluation with different settings to compare:

```python
import promptquality as pq

template = "Summarize: {{text}}"
data = {"text": ["Long article text here..."]}

for temp in [0.0, 0.5, 1.0]:
    pq.run(
        project_name="temperature-comparison",
        template=template,
        dataset=data,
        settings=pq.Settings(
            model_alias="ChatGPT (16K context)",
            temperature=temp,
            max_tokens=200,
        ),
    )
```

## Evaluation Runs with Custom Workflows

Log multi-step workflows for evaluation with specific scorers:

```python
from promptquality import EvaluateRun
import promptquality as pq

pq.login()

metrics = [
    pq.Scorers.context_adherence_plus,
    pq.Scorers.completeness,
    pq.Scorers.toxicity,
]

evaluate_run = EvaluateRun(
    run_name="rag-evaluation",
    project_name="rag-project",
    scorers=metrics,
)

test_queries = [
    {"input": "What is machine learning?", "context": "ML is a subset of AI..."},
    {"input": "Explain neural networks", "context": "Neural networks are..."},
]

for item in test_queries:
    output = your_rag_pipeline(item["input"], item["context"])
    evaluate_run.add_single_step_workflow(
        input=item["input"],
        output=output,
        context=item["context"],
        model="gpt-4o",
    )

evaluate_run.finish()
```

## Multi-Step Workflow Evaluation

For complex pipelines with retrieval and generation steps:

```python
from promptquality import EvaluateRun
import promptquality as pq

pq.login()

evaluate_run = EvaluateRun(
    run_name="multi-step-eval",
    project_name="agent-project",
    scorers=[pq.Scorers.context_adherence_plus, pq.Scorers.chunk_attribution],
)

query = "What are the benefits of RAG?"
retrieved_docs = retriever.search(query)
response = llm.generate(query, context=retrieved_docs)

evaluate_run.add_single_step_workflow(
    input=query,
    output=response,
    context=retrieved_docs,
    model="gpt-4o",
)

evaluate_run.finish()
```

## Best Practices for Evaluation

1. **Use meaningful project names** that reflect the experiment purpose.
2. **Run multiple evaluation sets** across different data distributions to catch edge cases.
3. **Compare scorer results** across runs to track quality improvements over time.
4. **Include context** in RAG evaluations so context-dependent metrics (Context Adherence, Chunk Attribution) can be computed.
5. **Use `EvaluateRun.finish()`** to ensure all results are uploaded and scored.
