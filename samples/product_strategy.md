# Meridian Motors Connected Vehicle Platform — Q3 Product Strategy (Driver Experience Track)

**Author:** Sarah Chen, VP Connected Experience
**Status:** Draft for executive review
**Target:** Q3 FY26 (July – September)
**Audience:** Engineering, product, and dealer operations leadership

---

## Background

In Q2 we improved remote command success rates by 14% through connectivity resilience improvements and reduced driver app crash rates by half. Driver satisfaction scores held flat. The next inflection point will come from solving the experience problems that surface *during the connected journey* and *across service channels* — places where our two largest owner segments (EV drivers, warranty-active owners) feel friction on every interaction.

Voice-of-owner data from the last 90 days converges on five themes. Three of them are P0 for Q3. Two are P1 candidates depending on capacity.

---

## P0 — Must ship by end of Q3

### 1. OTA update resilience under CDN saturation

**The problem.** When a deployment wave exceeds CDN throughput limits, vehicles in the batch stall in "Update Pending" with the infotainment system unresponsive. The Southwest cluster experienced a 40-minute outage window last month affecting roughly 8,000 vehicles. Direct owner NPS impact: -18 for affected vehicles in the 48 hours following a failed update night. Indirect: owners who associate the brand with unexpected downtime.

**The goal.** OTA deployments adopt staged rollout rings with per-ring throttle controls. Vehicles that stall must resume normal infotainment operation within 60 seconds. Downloads checkpoint at the TCU so a resumed session continues from byte offset rather than restarting the full package.

**Constraints.** ISO 26262 prohibits automatic rollback for safety-critical ECU updates without a validated rollback image. Rollback path must be pre-qualified for each target ECU before deployment authorisation.

**Success metric.** Zero "vehicle infotainment unresponsive due to update stall" incidents during the next major deployment wave, measured via telemetry. Synthetic test: saturate the CDN throttle artificially, confirm 100% of vehicles return to normal operation within 60 seconds.

### 2. Warranty claim unification

**The problem.** Owners can submit a warranty claim via the driver app OR walk into a dealership and have the service advisor enter it directly. These two intake channels write to different systems with no real-time reconciliation. Owners regularly arrive for service expecting their part is on order when it isn't, or vice versa. The dealer helpline spends an estimated 20% of its call volume simply disambiguating claim status.

**The goal.** Both channels become writes to **RecallHub**, the system of record. The owner sees a single claim status (submitted / parts ordered / ready for drop-off) regardless of intake channel. Status changes trigger a push notification to the verified contact method.

**Constraints.** GDPR and CCPA: consent-based notifications only — stored on the vehicle record, sent to the owner's verified contact (not the fleet/household default), audit log retained 7 years.

**Success metric.** Dealer helpline call volume for "where is my warranty claim" drops by 50% within 60 days of launch.

### 3. Navigation search — live charger availability

**The problem.** Navigation POI search does not incorporate real-time charger network status. Drivers search for charging options, see "Available" results, drive to the station, and find it offline or full. NPS for drivers who hit this is -32; for drivers who don't it's +20.

**The goal.** Search results are re-ranked by verified live availability from the charging network feed. When the top result shows low or no availability, surface in-range alternatives inline — not after the driver has already started routing.

**Constraints.** Sponsored charging network placement boost requires disclosure and Legal sign-off (advertising compliance). Maintain the 800ms p95 navigation search latency budget.

**Success metric.** 30-day rolling NPS for navigation sessions that end at a charging station improves to +12 minimum from the current -6 chain-wide average.

---

## P1 — Stretch goals for Q3

### 4. Connected services subscription transparency

A modest UX addition. Owners don't understand when their included trial ends or what features they will lose when it does. We add a "subscription status" card in the driver app showing: current tier, included features, trial end date (if applicable), and renewal path. Owner feedback from the last cohort survey suggests this lands well even as a small change.

**Success metric.** Owner support contact rate for "why did I lose a feature" drops 60% within 90 days of launch.

### 5. Gen1 TCU hardware capability gating

Our 2018–2020 vehicles run the Gen1 TCU which limits what we can build for those owners. A hardware service campaign is approved for FY26 but full coverage won't be reached until Q1 FY26. In Q3 we should ensure any *new* connected feature is explicitly tagged with its hardware floor — Gen2 only, or Gen1-compatible with fallbacks — so we don't silently break older vehicles.

This is more a discipline than a feature: every new connected-feature story must declare its TCU generation floor.

---

## Out of scope for Q3 (explicitly)

- **In-vehicle payment for drive-through.** Hardware project owned by OEM HW team, not platform engineering.
- **Dealer inventory portal redesign.** Slated for FY27 H1.
- **B2B fleet telematics dashboard.** Still in research; no decision before Q4.
- **Multi-language driver app (Spanish, French).** In flight (AD-096) but not a Q3 commitment.

---

## Cross-cutting expectations

- Every Q3 story must trace to a driver-facing outcome or a constraint forcing function. Pure tech-debt items continue to be funded out of the engineering capacity reserve, not the OKR-attributed capacity.
- Compliance review (Legal + InfoSec) is mandatory for: claim notifications (GDPR/CCPA), partner placement boost (advertising), and any new payment flow (PCI).
- Architecture Review Board (ARB) sign-off required for any deviation from the constraints in the engineering architecture wiki.

---

## What I'm asking engineering to do next

1. Synthesize this strategy into a structured Q3 backlog: epics → stories → tasks.
2. Cross-check against the existing JIRA/GitHub items so we don't redo work that's already planned.
3. Surface any **gaps** — capabilities I implied here that neither this strategy nor the existing backlog covers.
4. Surface any **conflicts** with the architecture constraints early.

I want this back by the next steering meeting in two weeks so we can sequence the Q3 calendar.
