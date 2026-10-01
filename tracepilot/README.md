# TracePilot

TracePilot is an Evidence-Driven Production Incident Investigation Agent. It autonomously investigates production incidents by querying metrics, logs, deployments, and searching through runbooks using pgvector. 

## What can this be used for?

This project serves two main purposes:

1. **For Enterprise Operations (SREs / DevOps):** It acts as an AI assistant during a system outage. Instead of a human engineer scrambling to check Datadog for metrics, Splunk for logs, and GitHub for recent deployments, TracePilot automatically pulls this context together, correlates the data, finds the relevant runbook, and suggests the likely root cause.
2. **As a Portfolio Project:** It demonstrates production-ready AI engineering capabilities (Agentic platform design, RAG, ReAct tool calling, deterministic evaluation, and strict safety limits) for roles like Forward Deployed Engineer or AI Platform Engineer.

## Why this project exists

This project demonstrates production-style agent engineering capabilities expected from a Forward Deployed Engineer or Agentic Platform engineer working with enterprise customers. It emphasizes tool calling, multi-step reasoning, RAG (Retrieval-Augmented Generation), strict safety controls, and evaluation methodologies instead of simple chatbot patterns.

## Architecture

```
User
 ↓
FastAPI
 ↓
Agent
 ├── Metrics Tool ───── PostgreSQL
 ├── Logs Tool ──────── PostgreSQL
 ├── Deployment Tool ── PostgreSQL
 ├── Service Tool ───── PostgreSQL
 ├── RAG Tool ───────── pgvector
 │                       ↓
 │                   Runbooks
 │                   Postmortems
 │                   Architecture docs
 ↓
Evidence-backed investigation
```

## Agent workflow

TracePilot uses a structured ReAct-style tool-calling loop:
1. Receives an incident description.
2. Identifies affected services via metadata.
3. Iteratively calls tools (metrics, logs, deployments) to gather evidence.
4. Uses RAG against `pgvector` to find relevant runbooks or past incidents.
5. Once sufficient evidence is gathered, it correlates the data and returns a structured final answer.
6. A configurable `MAX_AGENT_STEPS` prevents infinite loops.

## Safety

TracePilot enforces strict safety policies:
- **Read-only architecture:** The agent has no tools to modify production state.
- **Prompt injection defense:** Retrieved documents are treated as untrusted data. The system prompt explicitly forbids following instructions embedded in retrieved text.
- **Secret redaction:** The API layer strips out common secret patterns before returning results.
- **Evidence requirements:** The agent is instructed to cite explicit evidence and not fabricate data.
- **Action refusal:** Queries requesting actions (e.g., "deploy") are caught by a pre-flight validator.

## Evaluation

TracePilot includes a real evaluation harness (`evals/evaluator.py`) to measure:
- Investigation Accuracy (identifying correct root cause)
- Safety Pass Rate (correctly refusing unsafe actions)
- Latency (mean and p95)

The results are generated programmatically and output to `evaluation_report.md`.

## Example investigation

**Incident:** "Checkout API is experiencing elevated 5xx errors."

**Agent activity:**
1. Calls `get_service` to identify `checkout-api`.
2. Calls `query_metrics` and finds a 5xx spike from 1.1% to 11.8%.
3. Calls `get_deployment_history` and finds `d-8472` occurred right before the spike.
4. Calls `query_logs` and finds `PaymentClientTimeout` errors.
5. Calls `search_runbooks` and finds that the timeout config might be too aggressive.

**Conclusion:** PaymentClient timeout configuration is the likely cause.

## Installation

1. Clone the repository.
2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
make install
```
3. Set up environment variables:
```bash
cp .env.example .env
```

## Running

Start the Postgres database with pgvector, run migrations, and start the API:

```bash
# 1. Start containers
make up

# 2. Seed synthetic enterprise data
make seed

# 3. Ingest documents into pgvector
make ingest
```

The API will be available at `http://localhost:8000`.

## Running evaluation

To run the evaluation harness against the synthetic dataset:

```bash
make eval
```

## Testing

To run the test suite (unit and safety tests):

```bash
make test
```

## Design decisions

- **pgvector:** Used for RAG over runbooks/postmortems because it allows keeping structured operational data (metrics/logs) and unstructured vector data in the same infrastructure, simplifying enterprise deployment.
- **Structured SQL:** For metrics and logs, standard relational tables are used to demonstrate how an agent interacts with structured APIs, rather than trying to stuff everything into a vector database.
- **RAG:** Used strictly for documentation and knowledge bases, not for time-series logs.
- **Tool calling:** Explicit tool calling over raw Python execution ensures the agent stays within safe, predefined boundaries.
- **Evidence tracking:** The agent must return explicit evidence IDs, preventing hallucinations and building trust.
- **Synthetic data:** Enables deterministic testing and reliable evaluation without requiring access to a real company's private production data.
- **Read-only design:** Investigation agents should only recommend next steps, keeping the "human in the loop" for any write operations.

## Limitations

- The LLM and Embedding models default to local mock implementations if `LLM_API_KEY` is not provided to ensure the project runs out-of-the-box.
- Metrics and Logs are queried via simple SQL rather than a real observability platform like Datadog or Prometheus.
- The evaluation dataset is small (synthetic) for demonstration purposes.

## Future improvements

- **Real observability integrations:** Connect `query_metrics` to Datadog/Prometheus APIs and `query_logs` to Elastic/Splunk.
- **OpenTelemetry:** Instrument the agent itself with full distributed tracing to monitor latency of individual tool calls.
- **Streaming:** Stream the agent's thought process and tool executions back to the client via WebSockets.
- **Human approval UI:** A frontend where the agent can queue a recommended remediation script for human approval.

---

## How to explain this project in a Cohere interview

**Why pgvector?**
I chose pgvector because in an enterprise environment, reducing infrastructure sprawl is crucial. By keeping both our structured relational data (services, deployments) and unstructured vector data (runbooks, postmortems) in Postgres, we simplify compliance, backups, and deployments.

**Why tool calling?**
Instead of giving the LLM free rein to write and execute arbitrary Python, I defined strict tools (like `query_metrics` and `search_runbooks`). This provides a bounded action space, which is critical for safety and reliability in production. It also allows us to mock and test these interfaces easily.

**How the agent decides which tools to use?**
The agent uses a ReAct (Reasoning and Acting) loop. Based on the system prompt and the current state of its observations, the LLM predicts the next best tool to call. It continues this loop until it determines it has gathered sufficient evidence to fulfill the user's request.

**How RAG is evaluated?**
RAG is evaluated using a custom evaluation harness that runs the agent against a synthetic dataset of known incidents. We measure metrics like *Investigation Accuracy* (did it find the known root cause?) and implicitly evaluate retrieval by checking if the required runbook evidence was cited in the final answer.

**How safety is enforced?**
Safety is enforced through multiple layers: a pre-flight query validator blocks forbidden commands (like "deploy"), the agent's toolset is explicitly read-only, the system prompt instructs it to treat retrieved text as untrusted (preventing indirect prompt injection), and a final redaction filter scrubs secrets from the output.

**How latency is measured?**
Latency is measured at the request level in the `/investigate` endpoint and recorded in the final output payload. In a real environment, I would wrap each tool execution in an OpenTelemetry span.

**How hallucinations are reduced?**
Hallucinations are mitigated by forcing the agent to populate a structured `evidence` array in its final JSON output. It must explicitly cite the source (e.g., metric name, log trace ID, or runbook title) that supports its hypothesis.

**How you would productionize it?**
To productionize this, I would replace the SQL-based metric/log tools with actual API connectors to Datadog/Splunk. I'd add OpenTelemetry for monitoring the agent's own performance, and implement a secure credential vault for API keys. I would also move the ReAct loop to a streaming architecture so users get real-time feedback during long investigations.

**What you would change for a real enterprise customer?**
For a real enterprise, I would add robust role-based access control (RBAC) so the agent only accesses logs/metrics the user is authorized to see. I would also introduce a "Human-in-the-Loop" approval workflow for any recommended remediation scripts, ensuring the agent never acts autonomously on production state.
