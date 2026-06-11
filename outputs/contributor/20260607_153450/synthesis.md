# Backlog Synthesis

*Synthesized from: meeting_notes.txt*

## Summary

The meeting discussed various customer-facing problems and needs for Q3, including POS outages during peak hours, mobile app search issues with out-of-stock items, pharmacy refill confusion, loyalty tier uncertainty, and store-associate handheld scanner limitations.

## Epics (1)

### Epic 1: Point of Sale and Inventory Management

Enabling offline cash sales with local SKU pricing validation and upgrading store associate handheld inventory scanners to a modern platform.

#### 1.1 Enable offline cash sales with local SKU pricing validation

**Priority:** High   |   **Tags:** `pos` `offline-mode` `inventory`

> The current POS system cannot process cash sales when the WAN is down because it cannot validate SKU pricing locally. This story aims to enable local SKU pricing validation to allow cash sales to proceed offline.

**User story**
- As a store associate, I want to process cash sales even when the store's internet connection is down, so that we can avoid lost revenue and serve customers without interruption.

**Acceptance criteria**
- Given the store's WAN connection is down, when a store associate attempts a cash sale, then the POS system processes the sale.
- Given the store's WAN connection is down, when a store associate attempts a cash sale, then the system validates SKU pricing using local data.
- Given the WAN connection is restored after offline cash sales, when the POS reconnects, then all offline cash transactions are synchronized with central systems.

**Tasks**
- ST-01-TK-01: Implement local SKU pricing validation for cash sales in POS system
- ST-01-TK-02: Upgrade store associate handheld inventory scanners to modern platform

#### 1.2 Upgrade store associate handheld inventory scanners to a modern, secure platform

**Priority:** High   |   **Tags:** `store-associate` `inventory` `security` `hardware`

> The current store-associate handheld inventory scanners run on an outdated operating system (Android 7) that can no longer receive security patches.

**User story**
- As a store associate, I want to use modern, secure handheld scanners, so that I can efficiently manage inventory and serve customers without security risks or operational limitations.

**Acceptance criteria**
- Given a store associate uses the new handheld scanner, when they perform inventory tasks, then the device operates on a supported and patched operating system.
- Given a store associate uses the new handheld scanner, when they access inventory data, then the device provides modern features for efficient management.
- Given the new handheld scanners are deployed, when a security scan is performed on the devices, then no critical or high-severity vulnerabilities related to an outdated OS are found.
- Given a store associate needs to look up customer information via the handheld, when the feature is used, then all customer identity interactions adhere to NSID federation requirements.

**Tasks**
- ST-05-TK-01: Upgrade handheld inventory scanner operating system to modern platform
- ST-05-TK-02: Implement customer identity features for new handheld scanners

---

## ♻️ Possible duplicates

New stories that overlap with existing JIRA / GitHub tickets.

- **Story ST-04** overlaps with **NS-389** (confidence: low)
  - Local-embedding cosine similarity 0.70 — new story title/description overlaps existing ticket "Loyalty tier downgrade email — reduce confusion".
