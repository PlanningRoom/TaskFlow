# Decision 004: Data Residency Scope

**Status:** Decided

**Category:** Platform & Topology

**Question:** In how many regions does TaskFlow store and serve data?

**Decision:** Single cloud region. All primary data storage and compute runs in one documented region, disclosed in the privacy policy.

**Rationale:** Inherited from BRD DI-03 and Business Decision 025. Multi-region deployment adds significant complexity (replication, consistency, failover) without benefit for a demonstration project. The specific region is selected in Decision 037.
