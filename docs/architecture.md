# Architecture — tarun-personal-mcp

## Overview

`tarun-personal-mcp` is a personal Model Context Protocol (MCP) server that aggregates Tarun Raja's Instagram photography, hiking trail history, travel destination reviews, and general personal facts into a single API surface callable by any MCP-compatible chatbot client.

The server runs as an AWS Lambda function (Python 3.12) fronted by API Gateway. [FastMCP](https://github.com/jlowin/fastmcp) handles MCP protocol negotiation and tool dispatch. [Mangum](https://github.com/jordaneremieff/mangum) bridges the FastMCP ASGI application to API Gateway's Lambda proxy event format, requiring no changes to the application layer to run serverlessly.

The entire stack is defined in a single AWS SAM template (`template.yaml`) and deployed from GitHub Actions via OIDC federation (no long-lived AWS credentials stored in CI).

---

## C4 Diagrams

All diagrams use the [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) standard library and can be rendered with PlantUML locally or in any compatible viewer.

### Level 1 — System Context

**File:** [`docs/diagrams/c4_context.puml`](diagrams/c4_context.puml)

Shows the two human actors (Tarun as owner, chatbot users as callers), the MCP server system, and the two external systems it integrates with: the Instagram Graph API (media source) and Amazon Bedrock (Claude claude-opus-4-5 for vision inference).

### Level 2 — Containers

**File:** [`docs/diagrams/c4_container.puml`](diagrams/c4_container.puml)

Zooms into the AWS stack. Every AWS resource from `template.yaml` appears as a container:

| Container | Type | Role |
|---|---|---|
| API Gateway (prod) | AWS REST API | TLS termination; proxy-integrates all paths/methods to Lambda |
| McpFunction | AWS Lambda (Python 3.12) | FastMCP + Mangum ASGI entrypoint; dispatches tool calls |
| CacheTable | DynamoDB (PAY_PER_REQUEST) | Keyed-by-media_id cache for vision summaries; TTL-managed expiry |
| DataBucket | S3 (private) | Static JSON data files for hiking and travel tools |
| Secrets Manager | AWS Secrets Manager | Instagram Graph API access token (`tarun/instagram-token`) |
| Amazon Bedrock | AWS-managed | Claude claude-opus-4-5 foundation model for image vision |

### Level 3 — Components

**File:** [`docs/diagrams/c4_component.puml`](diagrams/c4_component.puml)

Zooms into the Lambda function's `src/` directory. Each Python module is a component with its dependencies to sibling modules and external containers shown.

---

## Key Design Decisions

### FastMCP + Mangum bridge

FastMCP exposes an ASGI application. Mangum wraps it so the same code runs both locally (as a standard ASGI server) and on Lambda (receiving API Gateway proxy events). The Lambda handler is a single line:

```python
handler = Mangum(mcp.get_asgi_app(), lifespan="off")
```

`lifespan="off"` disables ASGI lifespan events, which Lambda does not support.

### PAY_PER_REQUEST DynamoDB billing

The `CacheTable` uses on-demand (`PAY_PER_REQUEST`) billing. The photography tool is called infrequently by a small audience, so provisioned throughput would result in paying for idle capacity. On-demand billing means the table costs nothing when idle and scales automatically under any burst.

### 30-day TTL cache for vision summaries

Generating a vision description requires downloading an image from Instagram and invoking Bedrock, which adds latency and cost. Summaries are cached in DynamoDB with a 30-day TTL. `helpers/cache.py` also performs an in-process TTL check to handle the DynamoDB window where expired items may not yet be physically deleted.

### Least-privilege IAM

The Lambda execution role is granted the minimum permissions required:

- `dynamodb:GetItem` + `dynamodb:PutItem` on the cache table ARN only
- `s3:GetObject` on the data bucket objects only (not `ListBucket`)
- `secretsmanager:GetSecretValue` on the `tarun/instagram-token` secret ARN only
- `bedrock:InvokeModel` + `bedrock:InvokeModelWithResponseStream` on all foundation models in all regions (`arn:aws:bedrock:*::foundation-model/*`) — broadened from a single-model, single-region ARN to allow flexibility in model selection across regions
- CloudWatch Logs write access scoped to the specific log group

Wildcard resources are avoided except for the Bedrock policy, which uses `arn:aws:bedrock:*::foundation-model/*` to allow all foundation models in all regions.

### OIDC GitHub Actions deploy

The SAM deployment uses GitHub Actions with OIDC federation to assume an IAM role. No AWS access keys are stored as GitHub secrets. The IAM role trust policy is scoped to the specific repository and branch.

---

## Data Flows

### 1. Photography — cache hit

1. Chatbot client calls `get_photography` (optionally with a `topic` filter) over HTTPS.
2. API Gateway proxies the request to the Lambda function.
3. Lambda / Mangum routes it to `tools/photography.py`.
4. `helpers/secrets.py` retrieves the Instagram token from Secrets Manager.
5. `photography.py` calls the Instagram Graph API to fetch the media list.
6. For each image, `helpers/cache.py` performs a `GetItem` on DynamoDB.
7. The cached summary is returned directly — no Bedrock call is made.
8. The tool returns a list of `{permalink, timestamp, caption, summary}` dicts.

### 2. Photography — cache miss (vision inference)

Steps 1–6 are identical to the cache-hit flow. On a miss:

7. `photography.py` downloads the image bytes from the Instagram `media_url` via `httpx`.
8. The bytes are base64-encoded and sent to Claude claude-opus-4-5 via the Anthropic SDK (`bedrock:InvokeModel` or `bedrock:InvokeModelWithResponseStream`).
9. Claude returns a 2–3 sentence description of the photo.
10. `helpers/cache.py` writes the summary to DynamoDB with a 30-day TTL.
11. The tool returns the newly generated summary alongside the image metadata.

### 3. Hiking / travel — S3 read

1. Chatbot client calls `get_hiking_activity` or `get_travel_reviews` (optionally with a filter string).
2. API Gateway → Lambda → respective tool module.
3. `helpers/s3_reader.py` calls `s3:GetObject` to download `hiking_data.json` or `travel_reviews.json` from the DataBucket.
4. The JSON list is parsed, optionally filtered in-process by the provided string, and returned.

No caching layer is involved; S3 `GetObject` latency is typically < 50 ms for small JSON files.

### 4. Personal facts — static in-process

1. Chatbot client calls `get_personal_facts` with an optional `category` argument.
2. API Gateway → Lambda → `tools/personal_facts.py`.
3. The function looks up the requested category in an in-process Python dict (`FACTS`).
4. One category dict or the full four-category dict is returned immediately.

No AWS service calls are made for this tool.

---

## AWS Resources

| SAM Resource | AWS Type | Key Properties |
|---|---|---|
| `McpApi` | `AWS::Serverless::Api` | Stage: `prod`; proxy integration `ANY /{proxy+}` |
| `McpFunction` | `AWS::Serverless::Function` | Runtime: Python 3.12; Handler: `server.handler`; Memory: 512 MB; Timeout: 30 s |
| `CacheTable` | `AWS::DynamoDB::Table` | Hash key: `media_id` (S); BillingMode: `PAY_PER_REQUEST`; TTL attribute: `ttl` |
| `DataBucket` | `AWS::S3::Bucket` | Name: `tarun-personal-mcp-data-<AccountId>`; all public access blocked |

Secrets Manager secret (`tarun/instagram-token`) is referenced by ARN but not declared in the SAM template — it is created manually and referenced by the IAM policy.

---

## MCP Tools Reference

| Tool Function | Module | Input | Output |
|---|---|---|---|
| `get_photography` | `tools/photography.py` | `topic: str = ""` — case-insensitive caption filter | `list` of up to 5 dicts: `{permalink, timestamp, caption, summary}` |
| `get_hiking_activity` | `tools/hiking.py` | `trail_name: str = ""` — case-insensitive trail name filter | `{"trails": [...]}` — each trail: `{name, distance_miles, elevation_ft, date, rating, notes}` |
| `get_travel_reviews` | `tools/travel.py` | `location: str = ""` — case-insensitive place filter | `{"reviews": [...]}` — each review: `{place, country, rating, review, date, highlights}` |
| `get_personal_facts` | `tools/personal_facts.py` | `category: str = ""` — one of `photography`, `hiking`, `travel`, `work` | Single-category dict or full four-category dict; no I/O |
