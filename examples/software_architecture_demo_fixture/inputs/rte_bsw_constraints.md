# EPS Demo RTE and BSW Constraints

Document status: project source for this demo fixture.

## OS Tasks (Candidate)

| Task | Period | Priority | Runnable group |
|---|---|---|---|
| OsTask_5ms | 5 ms | High | Assist control, I/O sampling |
| OsTask_10ms | 10 ms | Medium | Diagnostic coordination |

## BSW Modules (Architecture View)

| Module | Role in architecture |
|---|---|
| Com | Vehicle speed signal routing |
| Dcm | Diagnostic request handling |
| Dem | Event storage and status |

## Stack Hint

OsTask_5ms stack budget clue: 2 KB (platform document reference required for confirmation).
