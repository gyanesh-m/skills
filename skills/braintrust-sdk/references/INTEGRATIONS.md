# Framework Integrations

Braintrust integrates with popular LLM frameworks via built-in instrumentation packages. Most integrations require only an import — no manual wrapper code.

## Python Integrations

All integrations are included in the `braintrust` package. Import the integration module to activate auto-instrumentation.

### OpenAI

```python
from braintrust.oai import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI())

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
)
```

Minimum version: `openai>=1.71`

### Anthropic

```python
from braintrust.integrations.anthropic import wrap_anthropic
from anthropic import Anthropic

client = wrap_anthropic(Anthropic())

message = client.messages.create(
    model="claude-opus-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

Minimum version: `anthropic>=0.48.0`

### LangChain

```python
from braintrust.integrations.langchain import BraintrustCallbackHandler

handler = BraintrustCallbackHandler()

chain = build_langchain_chain()
result = chain.invoke({"question": "What is RAG?"}, config={"callbacks": [handler]})
```

Minimum version: `langchain-core>=0.3.28`

### PydanticAI

```python
from braintrust.integrations.pydantic_ai import instrument_pydantic_ai
import braintrust

instrument_pydantic_ai()

# All PydanticAI agent calls are now traced automatically
agent = Agent("openai:gpt-4o", system_prompt="You are a helpful assistant.")
result = await agent.run("What is the capital of France?")
```

Minimum version: `pydantic_ai>=1.10.0`

### Claude Agent SDK

```python
from braintrust.integrations.claude_agent_sdk import instrument_claude_agent_sdk
import braintrust

instrument_claude_agent_sdk()

# All claude_agent_sdk calls are now traced
import claude_agent_sdk
result = await claude_agent_sdk.run("Write a haiku about observability.")
```

Minimum version: `claude_agent_sdk>=0.1.10`

### DSPy

```python
from braintrust.integrations.dspy import instrument_dspy
import dspy

instrument_dspy()

lm = dspy.LM("openai/gpt-4o")
dspy.configure(lm=lm)

# All DSPy programs are now traced
predictor = dspy.Predict("question -> answer")
result = predictor(question="What is DSPy?")
```

Minimum version: `dspy>=2.6.0`

### LiteLLM

```python
from braintrust.integrations.litellm import instrument_litellm
import litellm

instrument_litellm()

response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

Minimum version: `litellm>=1.74.0`

### Google GenAI

```python
from braintrust.integrations.google_genai import instrument_google_genai
import google.generativeai as genai

instrument_google_genai()

model = genai.GenerativeModel("gemini-1.5-pro")
response = model.generate_content("Explain machine learning.")
```

Minimum version: `google-genai>=1.30.0`

### Google ADK

```python
from braintrust.integrations.adk import instrument_adk

instrument_adk()

# All Google ADK agent calls are now traced
```

Minimum version: `google-adk>=1.14.1`

### OpenRouter

```python
from braintrust.integrations.openrouter import instrument_openrouter
import openrouter

instrument_openrouter()
```

Minimum version: `openrouter>=0.6.0`

### pytest Plugin

Braintrust includes a pytest plugin for running evals as standard test suites:

```python
# conftest.py
pytest_plugins = ["braintrust.wrappers.pytest_plugin"]
```

```bash
pytest evals/ --braintrust-api-key=$BRAINTRUST_API_KEY
```

Minimum version: `pytest>=8`

---

## TypeScript / JavaScript Integrations

### Auto-Instrumentation (Node.js runtime hook)

Instruments OpenAI, Anthropic, Vercel AI SDK, and others automatically:

```bash
node --import braintrust/hook.mjs app.js
```

No code changes required.

### LangChain.js

```typescript
import { BraintrustCallbackHandler } from "@braintrust/langchain-js";
import { ChatOpenAI } from "@langchain/openai";
import { StringOutputParser } from "@langchain/core/output_parsers";

const handler = new BraintrustCallbackHandler();

const model = new ChatOpenAI({ callbacks: [handler] });
const parser = new StringOutputParser();

const chain = model.pipe(parser);
const response = await chain.invoke("What is LangChain?");
```

Install: `npm install @braintrust/langchain-js`

### OpenAI Agents (JS)

```typescript
import { BraintrustTracer } from "@braintrust/openai-agents";
import { Agent, run } from "@openai/agents";

const agent = new Agent({
  name: "my-agent",
  instructions: "You are a helpful assistant.",
  tracer: new BraintrustTracer(),
});

const result = await run(agent, "Hello!");
```

Install: `npm install @braintrust/openai-agents`

### OpenTelemetry

```typescript
import { BraintrustSpanProcessor } from "@braintrust/otel";
import { NodeSDK } from "@opentelemetry/sdk-node";

const sdk = new NodeSDK({
  spanProcessors: [new BraintrustSpanProcessor()],
});

sdk.start();
```

Install: `npm install @braintrust/otel`

### Temporal

```typescript
import { BraintrustPlugin } from "@braintrust/temporal";
import { Worker } from "@temporalio/worker";

const worker = await Worker.create({
  interceptors: {
    workflowModules: [BraintrustPlugin.workflowInterceptors],
  },
  // ...
});
```

Install: `npm install @braintrust/temporal`

### Browser

```typescript
import { init } from "@braintrust/browser";

const experiment = await init("my-project");

experiment.log({
  input: { query: "Hello" },
  output: "Hi there!",
  scores: { accuracy: 1.0 },
});
```

Install: `npm install @braintrust/browser braintrust`
