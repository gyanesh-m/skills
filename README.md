# Galileo Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-agentskills.io-blue)](https://agentskills.io)

**Agent Skills for the Galileo AI platform** — give your AI coding assistant the knowledge to work with Galileo's evaluation, observability, and guardrails SDKs.

## Quick Start

Install all Galileo skills into your project:

```bash
npx add-skill gyanesh-m/skills
```

Install a specific skill:

```bash
# Python SDK skill
npx add-skill gyanesh-m/skills --skill galileo-python-sdk

# TypeScript SDK skill
npx add-skill gyanesh-m/skills --skill galileo-typescript-sdk
```

Target a specific AI assistant:

```bash
npx add-skill gyanesh-m/skills --agent cursor
npx add-skill gyanesh-m/skills --agent claude
```

## Supported AI Coding Assistants

| Assistant | Supported | Skills Directory |
|---|---|---|
| Claude Code | ✅ | `.claude/skills/` |
| Cursor | ✅ | `.cursor/skills/` |
| GitHub Copilot | ✅ | `.github/skills/` |
| OpenAI Codex | ✅ | `.agents/skills/` |
| Gemini CLI | ✅ | `.gemini/skills/` |
| Amp | ✅ | `.amp/skills/` |
| Roo Code | ✅ | `.roo/skills/` |
| OpenCode | ✅ | `.opencode/skills/` |

## Available Skills

### `galileo-python-sdk`

Complete reference for the Galileo Python SDK (`pip install galileo`). Covers:

- Observability and tracing with `galileo_context` and the `@log` decorator
- Wrapped OpenAI client for automatic tracing
- Evaluation experiments with `promptquality`
- Runtime guardrails with `galileo-protect`
- Framework integrations: OpenAI, Anthropic, LangChain, LangGraph, CrewAI, PydanticAI, Strands Agents, Google ADK
- Guardrail metrics: Hallucination detection, Context Adherence, Toxicity, PII, Prompt Injection, and more

### `galileo-typescript-sdk`

Complete reference for the Galileo TypeScript/JS SDK (`npm install @rungalileo/galileo`). Covers:

- `GalileoEvaluateWorkflow` for evaluation runs with scoring
- `GalileoObserveWorkflow` for production monitoring
- LLM, retriever, and tool step logging
- Framework integrations: Vercel AI SDK, Mastra, LangGraph (JS)
- All guardrail metrics available in evaluate mode

## Manual Installation

If you prefer to install skills manually, copy the relevant `SKILL.md` and `references/` directory into your AI assistant's skills folder:

### Claude Code

```bash
mkdir -p .claude/skills/galileo-python-sdk
cp -r skills/galileo-python-sdk/* .claude/skills/galileo-python-sdk/
```

### Cursor

```bash
mkdir -p .cursor/skills/galileo-python-sdk
cp -r skills/galileo-python-sdk/* .cursor/skills/galileo-python-sdk/
```

### GitHub Copilot

```bash
mkdir -p .github/skills/galileo-python-sdk
cp -r skills/galileo-python-sdk/* .github/skills/galileo-python-sdk/
```

## What is Galileo?

[Galileo](https://galileo.ai) is an AI evaluation, observability, and guardrails platform. Their tagline: **"Evaluate, Observe, and Protect your GenAI applications."**

| Product | Description |
|---|---|
| **Galileo Evaluate** | Run evaluation experiments on prompts, models, RAG pipelines, and agents using built-in and custom metrics |
| **Galileo Observe** | Production observability for LLM/agent applications with tracing, spans, and metrics |
| **Galileo Protect** | Runtime guardrails that scan prompts and responses, blocking harmful outputs with rulesets and stages |
| **Guardrail Metrics** | Proprietary metrics like Hallucination Index, Context Adherence, Chunk Attribution, Toxicity, PII detection, and more |

## Example Usage

After installing the Galileo Python SDK skill, your AI assistant understands Galileo patterns:

**You:** "Help me add Galileo observability to my LangGraph agent"

**AI Assistant generates:**

```python
from galileo import galileo_context, log
from galileo.openai import openai

galileo_context.init(project="langraph-agent", log_stream="production")

client = openai.OpenAI()

@log
def agent_pipeline(user_input: str):
    context = retrieve_documents(user_input)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Context: {context}\n\n{user_input}"}],
        model="gpt-4o",
    )
    return response.choices[0].message.content

@log(span_type="retriever")
def retrieve_documents(query: str):
    return vector_store.similarity_search(query, k=5)

result = agent_pipeline("What are the benefits of RAG?")
galileo_context.flush()
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing new skills or improving existing ones.

## Resources

- **Galileo Documentation:** https://docs.galileo.ai
- **Galileo Console:** https://app.galileo.ai
- **Python SDK:** https://github.com/rungalileo/galileo-python
- **TypeScript SDK:** https://github.com/rungalileo/galileo-js
- **SDK Examples:** https://github.com/rungalileo/sdk-examples
- **Agent Skills Spec:** https://agentskills.io

## License

[MIT](LICENSE)
