# ApexDrive Connected Vehicle Platform — Engineering Architecture Constraints

**Owner:** Architecture Review Board
**Last reviewed:** March 2026
**Audience:** All vehicle software and platform engineering teams. This page captures the constraints any new initiative must respect or formally exception out of.

---

## 1. Performance budgets

- **Driver app remote command latency p95** (e.g., remote climate, lock/unlock) must complete end-to-end under **3 seconds on an LTE connection**. We measure with synthetic transactions hourly. Regressions block release.
- **In-vehicle HMI response time** for a driver-initiated action (navigation search, media select) must stay under **200ms p95** at the head unit. If the cellular link is degraded, see Section 4.
- **Navigation POI search p95** in the driver app must stay under **800ms**. The search service is rate-limited at the edge to protect this budget.

## 2. Required integrations

- All vehicle and owner identity must flow through **VehicleIdentityService (VIS)**. New auth flows MUST NOT introduce a separate credential store. VIN-bound identity federation with VIS is the only supported pattern.
- All in-vehicle and in-app payment authorization MUST go through the **ConnectedPaymentGateway**. Direct calls to card processors are forbidden — this is a PCI scope requirement.
- All warranty and recall operations MUST go through the **RecallHub** service. RecallHub is the system of record for warranty claims and NHTSA-linked recall actions; writes to other stores cause reconciliation failures.

## 3. Security and compliance

- **PCI scope reduction.** Card data must never touch our application servers. ConnectedPaymentGateway hands back a tokenized reference; our code stores only the token.
- **GDPR / CCPA.** Any feature that surfaces a specific defect code, health condition linked to a recall, or precise location history requires:
  - Explicit owner consent stored on the vehicle record
  - Delivery only to the owner's *verified* contact method, never the shared fleet account default
  - Audit log of every notification sent, retained 7 years
- **UNECE WP.29 / ISO 21434 cybersecurity.** All OTA update packages must be cryptographically signed by the ApexDrive Code Signing Authority. Unsigned or self-signed packages must be rejected at the TCU.
- **ISO 26262 functional safety.** Updates to safety-critical ECUs (braking, steering, ADAS) require offline validation in the Hardware-in-the-Loop (HIL) test environment before any vehicle deployment. Automatic rollback of safety-critical updates is FORBIDDEN without a validated rollback image.
- **Advertising compliance.** Placement boost for charging networks or service partners based on commercial agreements requires disclosure and Legal review. Cannot ship without sign-off.

## 4. Offline tolerance (in-vehicle and connectivity loss)

- **Core driving functions** (navigation map rendering, climate control, media playback from local cache) MUST continue to operate when the cellular link is lost. No core driving feature may be cloud-dependent.
- **Remote commands** (lock/unlock, climate pre-condition, horn) that arrive while offline MUST be queued and executed within 60 seconds of connectivity restoration, provided they are still within their validity window.
- **Safety-critical features** (AEB, lane-keep, emergency call pre-trigger) MUST NEVER depend on cellular connectivity.
- **Gen1 TCU vehicles** (2018–2020 model years) cannot receive:
  - Differential (delta) OTA packages — full firmware images only, max 4 GB per update
  - TLS 1.3 connections — TLS 1.2 is the floor for Gen1
  - Background OTA downloads that run more than 90 minutes without user acknowledgement

Stories that depend on capabilities unavailable on Gen1 TCU must explicitly declare the hardware floor and either gate by VehicleGeneration or target Gen2 only.

## 5. Data residency

- Driver PII for EU owners must remain in our EU-West and EU-Central regions. Cross-region replication to US/APAC is forbidden under the current GDPR program.
- Telematics aggregates (no PII, anonymised) may flow to our central data warehouse in US-East.

## 6. Forbidden patterns

- **Polling vehicle telemetry** from the cloud at intervals shorter than 30 seconds. Use the telematics event stream instead.
- **Direct CAN bus writes** from any application-layer service. All actuator commands must go through the in-vehicle Gateway ECU with validated message authentication codes (MACs).
- **Custom encryption.** Use the platform KMS and our standard TLS/DTLS libraries. Rolling your own crypto is forbidden.
- **Direct database access** to the RecallHub warranty tables from non-RecallHub services. Use the RecallHub API.

## 7. Recommended defaults (should, not must)

- Feature flagging via LaunchDarkly for any change that touches a driver-facing surface
- Server-driven UI for any flow that changes more than monthly
- gRPC for service-to-service; REST only for external/partner APIs
- All new services emit OpenTelemetry traces by default

## 8. Hardware capabilities reference

| Hardware | Platform | Notes |
|---|---|---|
| Gen1 TCU (2018–2020) | Custom Linux, ARM Cortex-A7, 512 MB RAM | TLS 1.2 only; full OTA packages only; max 4 GB. Refresh Q1 FY26. |
| Gen2 TCU (2021+) | Custom Linux, ARM Cortex-A55, 2 GB RAM | TLS 1.3; differential OTA; background download |
| Head Unit (HMI) | Android Automotive OS 12+ | Navigation, media, settings; 3P app store gated |
| Dealer diagnostic tablet | Android 13, ruggedised | Technician tooling; must work on workshop Wi-Fi with no cellular |
| Driver companion app | iOS 16+, Android 9+ | Below floor = legacy maintenance mode only |

---

This page is updated quarterly. If your team needs an exception, file an ADR (Architecture Decision Record) tagged `exception:` and route it to the Architecture Review Board.
