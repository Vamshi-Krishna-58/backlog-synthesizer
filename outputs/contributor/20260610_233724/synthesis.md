# Backlog Synthesis

*Synthesized from: meeting_notes.txt*

## Summary

The Q3 planning meeting synthesized customer-facing problems, highlighting five key areas. These include POS system outages during peak hours requiring an offline mode, the mobile app's search functionality surfacing out-of-stock items, and significant customer confusion regarding pharmacy prescription refills due to disparate systems. Additionally, customers lack clarity on loyalty tier status changes, and there's a critical constraint regarding outdated store-associate handheld scanners running Android 7.

## Epics (2)

### Epic 1: Store Systems & Operational Resilience

This epic focuses on enhancing the reliability and functionality of critical in-store systems, including Point-of-Sale (POS) operations during network outages and ensuring compatibility of new store-associate tools with existing hardware infrastructure.

#### 1.1 Enable POS Offline Mode for Cash Sales

**Priority:** High   |   **Tags:** `pos` `offline-mode` `payments`

> Implement an offline mode for Point-of-Sale (POS) systems to allow basic cash transactions during WAN outages. This capability is specifically for cash sales, as card sales are noted in the source material as being constrained by PCI compliance and will remain online-only.

**User story**
- As a store associate, I want the POS system to process cash sales during a WAN outage, so that we can continue serving customers and prevent lost revenue.

**Acceptance criteria**
- Given a store experiences a WAN outage, when a store associate attempts a cash sale, then the POS system successfully processes the transaction.
- Given a store experiences a WAN outage, when a store associate attempts a card sale, then the POS system clearly indicates that card payments are unavailable.
- Given WAN connectivity is restored, when offline cash transactions exist, then these transactions are automatically synchronized with central systems.
- Given a WAN outage, when a store associate scans an item, then the POS system validates SKU pricing using locally cached data.

**Tasks**
- ST-01-TK-01: Design and implement local data store for SKU pricing and product information on POS.
- ST-01-TK-02: Develop POS application logic for processing cash sales in offline mode.
- ST-01-TK-03: Implement mechanism for storing offline cash transactions locally on POS.
- ST-01-TK-04: Develop synchronization service to upload offline transactions to central systems upon WAN restoration.
- ST-01-TK-05: Implement POS UI/UX to clearly indicate card payment unavailability during WAN outages.
- ST-01-TK-06: Develop automated tests for offline cash transaction processing and online synchronization.

#### 1.2 Ensure New Store Associate Tools are Compatible with Android 7 Handheld Scanners

**Priority:** Medium   |   **Tags:** `store-associate` `inventory`

> Any new tooling developed for store associates must be compatible with existing handheld inventory scanners, which run Android 7 and will not be replaced until FY26. This story ensures that new capabilities can be deployed and utilized by store associates without requiring immediate hardware upgrades.

**User story**
- As a store associate, I want new store-associate tools to be compatible with my current Android 7 handheld scanner, so that I can use them effectively without waiting for new hardware.

**Acceptance criteria**
- Given a new store-associate tool is developed, when it is deployed to an Android 7 handheld scanner, then it installs and functions correctly.
- Given a new store-associate tool is developed, when it is deployed to an Android 7 handheld scanner, then it does not rely on hardware capabilities beyond what Android 7 supports.
- Given a new store-associate tool is developed, when it is deployed to an Android 7 handheld scanner, then it meets acceptable performance standards for typical use cases.

**Tasks**
- ST-05-TK-01: Conduct a spike to identify specific Android 7 API limitations and performance considerations for common store-associate tool features.
- ST-05-TK-02: Define and document technical guidelines and best practices for Android 7 compatibility for new store-associate tool development.
- ST-05-TK-03: Set up and maintain an Android 7 test environment (physical devices or emulators) for compatibility testing.
- ST-05-TK-04: Develop a comprehensive compatibility testing checklist for new store-associate tools on Android 7.
- ST-05-TK-05: Integrate Android 7 compatibility checks and automated tests into the CI/CD pipeline for store-associate tools.

---

### Epic 2: Enhanced Customer Mobile Experience

This epic focuses on improving the customer experience within the mobile app by providing more accurate inventory information, streamlining pharmacy refill processes, and increasing transparency around loyalty program status.

#### 2.1 Integrate Local Inventory into Mobile App Search and Display Alternatives

**Priority:** High   |   **Tags:** `mobile-app` `inventory`

> Enhance the mobile app's search functionality to factor in local store inventory status when ranking results. For out-of-stock items, the system should accurately display 'in stock' badges and suggest available alternatives directly within the search results or product page.

**User story**
- As a mobile app user, I want search results to accurately reflect local store inventory and suggest alternatives for out-of-stock items, so that I don't get frustrated by unfulfillable orders.

**Acceptance criteria**
- Given a user searches for an item, when the item is out of stock at their selected local store, then the search results do not rank the out-of-stock item as a top result.
- Given a user views an item that is out of stock at their selected local store, when the item has available alternatives, then relevant alternatives are displayed inline.
- Given a user searches for an item, when the item is in stock at their selected local store, then the search result displays an accurate 'in stock' badge.
- Given a user adds an item to their cart that is out of stock at their selected local store, then the system prevents checkout or clearly notifies the user of the stock issue before checkout completion.

**Tasks**
- ST-02-TK-01: Develop or integrate API to retrieve real-time local store inventory status for mobile app.
- ST-02-TK-02: Modify search service to incorporate local inventory status into search result ranking algorithm.
- ST-02-TK-03: Implement mobile app UI to display 'in stock' badges and accurate inventory status on search results and product pages.
- ST-02-TK-04: Develop backend service to identify and suggest alternative products for out-of-stock items.
- ST-02-TK-05: Implement mobile app UI to display suggested alternatives inline on product pages and potentially search results.
- ST-02-TK-06: Update checkout flow to validate cart items against local inventory and prevent/notify for out-of-stock items.
- ST-02-TK-07: Develop comprehensive QA test cases for inventory-aware search, alternatives display, and checkout validation.

#### 2.2 Unify Pharmacy Prescription Refill Records and Notifications

**Priority:** High   |   **Tags:** `pharmacy` `mobile-app` `compliance`

> Unify the prescription refill processes from the mobile app and IVR phone line into a single, reconciled system. This includes providing clear status updates to customers and enabling push notifications for ready prescriptions, ensuring compliance with HIPAA regulations for all notification content.

**User story**
- As a pharmacy customer, I want my prescription refill requests to be unified across all channels and receive clear status updates, so that I know when my prescription is ready without confusion.

**Acceptance criteria**
- Given a customer initiates a refill via the mobile app, when the pharmacy checks their system, then the refill request is visible and accurately recorded.
- Given a customer initiates a refill via the IVR phone line, when the pharmacy checks their system, then the refill request is visible and accurately recorded.
- Given a prescription is ready for pickup, when the customer has opted for notifications, then they receive a push notification with HIPAA-compliant content.
- Given a customer views their prescription status in the mobile app, when the status changes (e.g., 'processing', 'ready for pickup'), then the app displays the updated status accurately.

**Tasks**
- ST-03-TK-01: Conduct a spike to map existing mobile app and IVR refill workflows and identify data discrepancies.
- ST-03-TK-02: Design and implement a unified backend service/API for prescription refill requests and status management.
- ST-03-TK-03: Migrate mobile app refill submission and status retrieval to use the new unified pharmacy service.
- ST-03-TK-04: Update IVR system integration to submit refill requests and retrieve status from the new unified pharmacy service.
- ST-03-TK-05: Develop a push notification service for prescription status updates, ensuring HIPAA compliance for content.
- ST-03-TK-06: Implement mobile app UI to display real-time, unified prescription status updates.
- ST-03-TK-07: Develop end-to-end QA scenarios covering refill submission via both channels and notification delivery.

#### 2.3 Improve Loyalty Tier Transparency in Mobile App

**Priority:** Medium   |   **Tags:** `loyalty` `mobile-app`

> Enhance the mobile app to provide greater transparency regarding loyalty tier status, including clear rules for earning and losing tiers, and explicit communication about the timing of tier downgrades. This aims to reduce customer confusion and frustration.

**User story**
- As a loyalty program member, I want to clearly understand how I earn and lose loyalty tier status and the timing of any downgrades within the mobile app, so that I am not surprised or frustrated by changes.

**Acceptance criteria**
- Given a loyalty program member views their tier status in the mobile app, when they navigate to tier rules, then clear and concise criteria for earning and maintaining each tier are displayed.
- Given a loyalty program member is approaching a tier downgrade, when they view their status, then the app clearly communicates the impending downgrade and its effective date.
- Given a loyalty program member views their current tier, when they view their progress, then the app shows their progress towards the next tier or maintaining their current tier.
- Given a loyalty program member has been downgraded, when they view their status, then the app provides a clear explanation for the downgrade.

**Tasks**
- ST-04-TK-01: Develop or enhance backend API to expose loyalty tier rules, earning criteria, and maintenance requirements.
- ST-04-TK-02: Develop or enhance backend API to provide current loyalty tier status, progress towards next tier, and impending downgrade information.
- ST-04-TK-03: Implement mobile app UI to display detailed loyalty tier rules and criteria.
- ST-04-TK-04: Implement mobile app UI to show current tier status, progress, and visual indicators for tier changes.
- ST-04-TK-05: Implement mobile app UI to clearly communicate impending tier downgrades, including effective dates and reasons.
- ST-04-TK-06: Implement mobile app UI to provide clear explanations for past tier downgrades.
- ST-04-TK-07: Develop QA test cases for various loyalty member scenarios, including earning, maintaining, and losing tiers.

---

## 🔍 Gaps detected

Capabilities implied by the source material that are not represented in the existing backlog.

- **Offline Transaction Reconciliation** — The story enables offline cash transactions but does not address the critical process of reconciling these transactions with central systems (e.g., inventory, sales, finance) once network connectivity is restored. This is essential for data integrity and accurate reporting.
  - *Evidence:* Implement an offline mode for Point-of-Sale (POS) systems to allow basic cash transactions during WAN outages.
- **Logic for Suggesting Out-of-Stock Alternatives** — While the story mentions suggesting available alternatives for out-of-stock items, it doesn't explicitly cover the underlying logic, rules, or data sources required to generate these relevant suggestions. This is a distinct capability from merely displaying inventory status.
  - *Evidence:* For out-of-stock items, the system should accurately display 'in stock' badges and suggest available alternatives directly within the search results or product page.
- **Unified Pharmacy Refill Data Management** — The story focuses on unifying refill processes and notifications, but it doesn't explicitly address the underlying data architecture, migration, or consolidation required to create a single, reconciled system for prescription refill records, ensuring HIPAA-compliant storage and access.
  - *Evidence:* Unify the prescription refill processes from the mobile app and IVR phone line into a single, reconciled system.
