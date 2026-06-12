# Backlog Synthesizer — Azure End-to-End User Flow

> Render in VS Code with the **Markdown Preview Mermaid Support** extension,
> or open on GitHub / any Mermaid-aware viewer.

---

## 1. Runtime User Flow

Shows exactly what happens from the moment a user opens a browser to receiving the synthesized backlog output.

```mermaid
sequenceDiagram
    autonumber

    actor User as 👤 User<br/>(Browser)
    participant CA_Ingress as 🌐 Azure Container Apps<br/>Ingress (HTTPS)<br/>*.azurecontainerapps.io
    participant App as 📦 Container App<br/>backlog-synthesizer<br/>Streamlit · port 8502
    participant Entra as 🔐 Microsoft Entra ID<br/>login.microsoftonline.com<br/>OAuth2 / OIDC
    participant ACR as 🗄️ Azure Container Registry<br/>meridianmotorsacr0452<br/>.azurecr.io
    participant Claude as ☁️ Anthropic API<br/>claude-sonnet-4-5
    participant Gemini as ☁️ Google AI API<br/>gemini-2.5-flash
    participant Jira as 🎫 Jira Cloud<br/>atlassian.net

    Note over User, Jira: ── FIRST VISIT: Cold Start ──

    User->>CA_Ingress: HTTPS GET /
    CA_Ingress->>App: Route to Container App<br/>(min-replicas=0 → scale up ~30s)
    App-->>CA_Ingress: 200 OK — Streamlit UI

    Note over User, Entra: ── AUTHENTICATION: Microsoft Entra ID SSO ──

    CA_Ingress-->>User: Streamlit login page
    User->>App: Click "Sign in with Microsoft"
    App->>App: generate_state_nonce()<br/>HMAC-SHA256 signed token<br/>(stateless — survives restarts)
    App-->>User: HTTP 302 → Entra ID authorize URL<br/>?client_id=…&state=<hmac-token>

    User->>Entra: GET /oauth2/v2.0/authorize
    Entra-->>User: Microsoft login page
    User->>Entra: Enter credentials + MFA
    Entra-->>User: HTTP 302 → https://<FQDN>/?code=…&state=<hmac-token>

    User->>CA_Ingress: GET /?code=AUTH_CODE&state=TOKEN
    CA_Ingress->>App: Forward callback
    App->>App: consume_state() — verify HMAC + TTL
    App->>Entra: POST /oauth2/v2.0/token<br/>{code, client_secret, redirect_uri}
    Entra-->>App: {access_token, id_token}
    App->>App: _verify_id_token() via JWKS<br/>RS256 signature check<br/>Extract name, email, role
    App-->>User: Authenticated — role: contributor / admin

    Note over User, Jira: ── INPUT PHASE ──

    User->>App: Upload transcript (.txt/.md/.pdf)<br/>+ architecture wiki (.md)<br/>+ existing backlog (JIRA JSON)
    App->>App: InputSanitizer — 8 injection rules<br/>PII redaction · toxicity check
    App->>App: Pre-run gates:<br/>rate limit → budget reserve<br/>dedup SHA-256 → semaphore

    Note over App, Jira: ── LANGGRAPH PIPELINE: 7 Nodes ──

    App->>Claude: Parser Agent<br/>Extract topics + summary
    Claude-->>App: topics[], summary

    App->>Claude: Constraint Agent<br/>Extract architectural rules
    Claude-->>App: constraints[]

    App->>Claude: Story Writer Agent<br/>Generate Given/When/Then stories
    Claude-->>App: stories[] (with AC + priority)

    App->>Claude: Epic Decomposer Agent<br/>Group stories into epics + tasks
    Claude-->>App: epics[] with tasks[]

    App->>Jira: GapDetector — list_all()<br/>(optional: live backlog fetch)
    Jira-->>App: existing_tickets[]
    App->>App: EmbeddingTool — find_duplicates()<br/>all-MiniLM-L6-v2 (local, no LLM)
    App->>Gemini: Gap Detector Agent<br/>Conflicts + gaps (max_tokens=8000)
    Gemini-->>App: {conflicts[], gaps[]}

    App->>App: OutputScanner — guardrail check<br/>Hallucination · bias · PII
    App->>App: settle_reservation(actual_cost)<br/>Prometheus metrics recorded

    Note over User, Jira: ── OUTPUT PHASE ──

    App-->>User: synthesis.json — Epics/Stories/Tasks<br/>synthesis.md — Human-readable report<br/>audit_trail.md — Compliance record
```

---

## 2. CI/CD Deployment Flow

Shows how a code change in GitHub becomes a running Container App on Azure.

```mermaid
flowchart TD
    classDef gh     fill:#24292E,stroke:#444,color:#fff,rx:6
    classDef acr    fill:#0078D4,stroke:#005A9E,color:#fff,rx:6
    classDef cae    fill:#0078D4,stroke:#005A9E,color:#fff,rx:6
    classDef ca     fill:#50E6FF,stroke:#0078D4,color:#333,rx:6
    classDef entra  fill:#7B68EE,stroke:#5A4DB0,color:#fff,rx:6
    classDef gate   fill:#E74C3C,stroke:#922B21,color:#fff,rx:6
    classDef check  fill:#27AE60,stroke:#1A7A45,color:#fff,rx:6

    DEV["👨‍💻 Developer\npush to main"]:::gh

    subgraph GH["  GitHub Actions  "]
        direction TB
        CI["🧪 ci.yml\nruff · pytest (3.11 + 3.13)\nbandit · pip-audit\nTruffleHog secret scan\nDocker build verify"]:::gh
        BUILD["🔨 Build & push → ACR\ndocker buildx\nmulti-stage Python 3.13\ncache-from: gha"]:::gh
        DEPLOY_S["📦 Deploy → Staging\naz containerapp update\nimage: sha-<commit>"]:::gh
        SMOKE["🔬 Smoke test\nAzure login + az CLI\nFetch FQDN directly\ncurl /_stcore/health\n12 × 10s = 2 min window"]:::gh
        DEPLOY_P["🚀 Canary deploy → Prod\nrevision-suffix: sha-XXXXXXXX\n10% traffic split"]:::gh
        VERIFY["✅ Verify canary\ncurl /_stcore/health\n12 × 15s = 3 min window"]:::gh
        PROMOTE["📈 Promote → 100%\naz ingress traffic set\ndeactivate old revisions"]:::gh
    end

    subgraph AZURE["  Azure (eastus)  "]
        direction TB

        subgraph RG["  Resource Group: rg-meridian-motors  "]
            direction TB

            ACR["🗄️ Azure Container Registry\nmeridianmotorsacr0452.azurecr.io\nSKU: Basic · admin-enabled\nStores: backlog-synthesizer:sha + :latest"]:::acr

            subgraph CAE["  Container Apps Environment: cae-meridian-motors  "]
                direction LR

                CA_S["📦 Container App — Staging\nbacklog-synthesizer-staging\nmin-replicas: 0 (scale-to-zero)\nmax-replicas: 1\ntarget-port: 8502\ningress: external HTTPS"]:::ca

                CA_P["🏭 Container App — Production\nbacklog-synthesizer-prod\nmin-replicas: 1\nmax-replicas: 3\ntarget-port: 8502\ningress: external HTTPS"]:::ca
            end

            SECRETS["🔑 Container App Secrets\nacr-password\nentra-client-secret\ngoogle-api-key\n(secretref: env vars)"]:::gate
        end

        ENTRA_REG["🔐 Microsoft Entra ID\nApp Registration\nclient_id + tenant_id\nRedirect URIs:\nhttps://<staging-FQDN>/\nhttps://<prod-FQDN>/"]:::entra
    end

    DEV -->|"git push main"| CI
    CI -->|"all checks pass"| BUILD
    BUILD -->|"docker push :sha"| ACR
    ACR -->|"image ref"| DEPLOY_S
    SECRETS -->|"secretref env vars"| CA_S & CA_P
    DEPLOY_S -->|"az containerapp update"| CA_S
    DEPLOY_S --> SMOKE
    SMOKE -->|"HTTP 200"| DEPLOY_P
    DEPLOY_P -->|"az containerapp update\n--revision-suffix sha-XXXXXXXX"| CA_P
    DEPLOY_P --> VERIFY
    VERIFY -->|"canary healthy"| PROMOTE
    PROMOTE -->|"100% traffic"| CA_P
    CA_S & CA_P -->|"pull image"| ACR
    CA_S & CA_P -->|"OAuth2 redirect / callback"| ENTRA_REG
```

---

## 3. Azure Resource Map

Static view of all Azure resources and how they relate.

```mermaid
graph TD
    classDef rg     fill:#F0F0F0,stroke:#999,color:#333,rx:4
    classDef acr    fill:#0078D4,stroke:#005A9E,color:#fff,rx:6
    classDef cae    fill:#50E6FF,stroke:#0078D4,color:#333,rx:6
    classDef ca     fill:#A8D8F0,stroke:#0078D4,color:#333,rx:6
    classDef entra  fill:#7B68EE,stroke:#5A4DB0,color:#fff,rx:6
    classDef ext    fill:#888,stroke:#555,color:#fff,rx:6
    classDef gh     fill:#24292E,stroke:#444,color:#fff,rx:6
    classDef secret fill:#E74C3C,stroke:#922B21,color:#fff,rx:6

    GH["GitHub\nVamshi-Krishna-58/backlog-synthesizer"]:::gh

    subgraph SUBSCRIPTION["  Azure Subscription  "]
        subgraph RG["  Resource Group: rg-meridian-motors (eastus)  "]
            ACR["Azure Container Registry\nmeridianmotorsacr0452.azurecr.io\nSKU: Basic"]:::acr

            subgraph CAE_BOX["  Container Apps Environment: cae-meridian-motors  "]
                CA_STAGING["Container App — Staging\nbacklog-synthesizer-staging\nscale: 0→1\nport 8502"]:::ca
                CA_PROD["Container App — Production\nbacklog-synthesizer-prod\nscale: 1→3\nport 8502"]:::ca
            end

            APP_SECRETS["App Secrets\nacr-password\nentra-client-secret\ngoogle-api-key"]:::secret
        end

        ENTRA["Microsoft Entra ID\nApp Registration\nTenant + Client ID\nJWKS key verification"]:::entra
    end

    subgraph EXTERNAL["  External Services  "]
        ANTHROPIC["Anthropic API\nclaude-sonnet-4-5\nclaude-haiku-4-5"]:::ext
        GOOGLE_AI["Google AI API\ngemini-2.5-flash\ngemini-2.5-pro"]:::ext
        JIRA["Jira Cloud\natlassian.net"]:::ext
        CONFLUENCE["Confluence Cloud\natlassian.net"]:::ext
    end

    GH -->|"push Docker image"| ACR
    GH -->|"az containerapp update"| CA_STAGING & CA_PROD
    ACR -->|"image pull"| CA_STAGING & CA_PROD
    APP_SECRETS -->|"secretref"| CA_STAGING & CA_PROD
    CA_STAGING & CA_PROD -->|"OAuth2 auth code flow"| ENTRA
    CA_STAGING & CA_PROD -->|"LLM API calls"| ANTHROPIC & GOOGLE_AI
    CA_STAGING & CA_PROD -->|"REST API"| JIRA & CONFLUENCE
```

---

## Azure Service Inventory

| Azure Service | Resource Name | Purpose |
|---|---|---|
| **Resource Group** | `rg-meridian-motors` (eastus) | Logical container for all project resources |
| **Azure Container Registry** | `meridianmotorsacr0452.azurecr.io` | Stores versioned Docker images (`:sha` + `:latest`), SKU Basic, admin-enabled |
| **Container Apps Environment** | `cae-meridian-motors` | Shared networking + compute plane for both Container Apps |
| **Container App — Staging** | `backlog-synthesizer-staging` | Pre-production app; scale-to-zero (min=0, max=1); target port 8502 |
| **Container App — Production** | `backlog-synthesizer-prod` | Live app; always-on (min=1, max=3); canary traffic splitting |
| **Microsoft Entra ID** | App Registration (tenant + client ID) | SSO via OAuth2 authorization code flow; HMAC-signed CSRF tokens; JWKS JWT verification |
| **Container App Secrets** | `acr-password`, `entra-client-secret`, `google-api-key` | Secrets injected as env vars via `secretref:` — never stored in image or workflow env |

## Key Deployment Facts

| Fact | Detail |
|---|---|
| **Trigger** | Every push to `main` → auto-deploy to staging; production requires manual `workflow_dispatch` |
| **Image tag** | `meridianmotorsacr0452.azurecr.io/backlog-synthesizer:<git-sha>` — one unique image per commit |
| **Staging scale** | `min-replicas=0` — container stops when idle; cold-start ~30s on first request |
| **Production scale** | `min-replicas=1` — always warm; up to 3 replicas under load |
| **Canary deploy** | New production revision gets 10% traffic; 3-minute health window; promotes to 100% on pass |
| **Smoke test** | Fetches staging FQDN directly via Azure CLI (not from job output, which is masked) |
| **CSRF protection** | Stateless HMAC-SHA256 signed state tokens — verified without server-side storage; survives scale-to-zero |
| **Redirect URI** | `ENTRA_REDIRECT_URI` dynamically injected from `az containerapp show … fqdn` at deploy time |
| **Secrets** | ACR password, Entra client secret, Google API key stored as Container App secrets; mounted as env vars via `secretref:` |
