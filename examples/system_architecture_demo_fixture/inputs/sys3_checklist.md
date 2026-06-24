# SYS.3 System Architecture Review Checklist

## ASPICE SYS.3 Alignment

- Upstream system requirements are identified and summarized as architecture inputs.
- Logical architecture decomposition is visible and traceable to upstream SYS IDs.
- Physical / technical architecture reflects ECU boundary and platform constraints.
- Architecture elements are uniquely identified and inventoried.
- Interface architecture includes direction, counterpart, and boundary notes.
- Requirement-to-architecture allocation matrix is present or open items are explicit.
- Diagnostic and degradation architecture links to provided diagnostic constraints.
- Verification method candidates are marked unless confirmed by source or HITL.
- Open communication and confirmation items are visible.

## System Architecture Quality

- Architecture blocks have clear responsibilities without duplicating SyRS wording as facts.
- Interface architecture aligns with interface specification source material.
- Resource and platform constraints reference provided platform source or open items.
- Each critical architecture claim has T0/T1 support or NEEDS_USER_CONFIRMATION.

## Functional Safety Boundary

- System Architecture does not introduce HARA conclusions, ASIL ratings, or Safety Goals.
- Safety-related architecture content only references provided FSR / SG / TSC source material.
- Final report is review-ready and is not an approval or compliance certification.

## With-Reference Boundary

- Reference architecture documents may guide structure and diagram shape only.
- Reference architecture content must not support architecture elements, allocation, interfaces, or conclusions.
- Delta analysis is required when a reference architecture document is supplied.
