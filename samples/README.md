# Sample inputs

These files describe a single fictional product — **Meridian Motors Connected Vehicle Platform**, a software platform powering connected vehicles for Meridian Motors, a fictional automotive OEM with ~500,000 active connected vehicles on the road — across the three input types the Backlog Synthesizer accepts.

The four source documents and two ticket exports cross-reference each other so the agents have genuine overlaps, conflicts, and gaps to find. A reviewer can verify the synthesis is correct by spot-checking these intentional flags.

## The Meridian Motors fiction in one paragraph

Meridian Motors is a fictional automotive OEM whose connected vehicle platform supports OTA firmware updates for ~500,000 vehicles, a driver companion app (iOS/Android), an EV charging integration layer, connected services subscriptions, a warranty and recall management system (**RecallHub**, the system of record for all warranty claims), a dealer portal for ~3,000 service centres, and technician tooling (dealer diagnostic tablets running Android 13 as well as a legacy Gen1 TCU fleet in 2018–2020 model-year vehicles).

## The files

| File | What it is | Notable details |
|---|---|---|
| `meeting_notes.txt` | Connected Vehicle Experience Q3 planning meeting transcript | Five themes raised; one (in-vehicle drive-through payment) explicitly declined; cross-references the architectural constraints in `architecture_constraints.md` and several existing JIRA tickets |
| `architecture_constraints.md` | Engineering architecture wiki page | Performance budgets, required integrations (VIS, ConnectedPaymentGateway, RecallHub), security rules (PCI, GDPR/CCPA, ISO 26262, UNECE WP.29), offline tolerance per hardware tier, and forbidden patterns |
| `product_strategy.md` | Q3 strategy document from the VP of Connected Experience | Same themes as the meeting notes but formal; tags P0 vs P1; explicitly excludes in-vehicle payment, dealer portal redesign, B2B fleet dashboard |
| `jira_backlog.json` | 30 existing JIRA tickets | Multiple intentional overlaps with the meeting notes (AD-412 charger availability, AD-419 VIN scraping, AD-227 Kafka migration). Triggers RAG path (≥20 items). |
| `github_issues.json` | 6 existing GitHub issues | A second source of existing work; some overlap with JIRA, some unique (e.g., #1041 remote climate GPS location) |

## Intentional flags the agents should find

When the synthesiser runs against these inputs together, here is what a correct run should produce:

### Duplicates (new story ↔ existing ticket)

| Topic from meeting notes | Should be flagged as duplicate of | Confidence |
|---|---|---|
| Navigation returns unavailable EV chargers | `AD-412` (in-progress) + GitHub `#1247` | High |
| Driver app polling for charger status | (n/a — surfaces from constraints, see "gaps" below) | — |
| Subscription tier confusion | `AD-389` (trial expiry email) + GitHub `#1102` | Medium-to-high |
| Remote climate wrong-vehicle dispatch | GitHub `#1041` | High |

### Conflicts (story ↔ architecture constraint)

| Story idea | Conflicts with constraint | Severity |
|---|---|---|
| "Auto-rollback safety-critical ECU updates" — anyone proposing this | "Automatic rollback of safety-critical updates is FORBIDDEN without a validated rollback image" (Section 3) | High |
| "Boost sponsored charging networks in navigation based on commercial deal" | "Placement boost requires disclosure and Legal review" (Section 3) | Medium |
| "Use Gen1 TCU background download for large firmware packages" | "Gen1 TCU background OTA downloads cannot run more than 90 minutes without user acknowledgement" (Section 4) | High if it doesn't gate by hardware |

### Gaps (implied but missing from both new stories and existing backlog)

The agents should also surface things the strategy/transcript *implies* but neither the new stories nor existing tickets cover. Examples a reviewer should expect:

- **Owner consent capture flow for warranty notifications** (the strategy mentions consent-based claim notifications but no story addresses *how* the owner opts in)
- **OTA stall detection and recovery heuristics** (offline resilience is mentioned but the *trigger* for declaring a stall and resuming normal operation isn't designed)
- **The audit log retention extension** (existing AD-321 covers this — so this is actually NOT a gap; the agent should recognise it's covered)

## Sample sizes and threshold behaviour

- `jira_backlog.json` has **30 tickets**, which is above the `RETRIEVAL_THRESHOLD=20` in `src/memory/store.py`. This triggers the embedding-based semantic search path.
- `github_issues.json` has only 6, so they're included in the LLM prompt directly without retrieval narrowing.

## How each sample is designed to be used

```bash
# Full run with all three sources:
python src/main.py \
    --transcript samples/meeting_notes.txt \
    --constraints samples/architecture_constraints.md \
    --backlog samples/jira_backlog.json

# Strategy document instead of meeting notes:
python src/main.py \
    --transcript samples/product_strategy.md \
    --constraints samples/architecture_constraints.md \
    --backlog samples/jira_backlog.json

# Smaller demo with no wiki:
python src/main.py --transcript samples/meeting_notes.txt
```
