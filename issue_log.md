# issue_log.md

## Removed Dummy Server
- **What:** Removed temporary gRPC dummy server (`src/orchestrator/dummy_grpc_server.py`) used for smoke tests.
- **Why:** Replaced by the real server; reduces confusion/surface area.
- **Impact:** Fewer moving parts; smaller image.
- **Commit:** TBD
- **Date:** TBD
- **Owner:** TBD

## Week 1 Fixes
| # | Commit  | Date       | Owner         | Summary                                                                                       |
|---|---------|------------|---------------|-----------------------------------------------------------------------------------------------|
| 1 | 0e45cb5 | 2025-06-25 | VaibhavTechie | Documented Stage 2: execution engine test and results                                         |
| 2 | a978dbf | 2025-06-25 | VaibhavTechie | Tested and Documented configuration of stage 1 parser test with actual test script and output |
| 3 | eca3f41 | 2025-06-25 | VaibhavTechie | Initial Docker setup and project scaffolding                                                  |
| 4 | a6cf407 | 2025-06-25 | VaibhavTechie | Initial project structure and empty files for orchestrator                                    |


## Known Issues / Follow-ups
- Standardize gRPC stub imports (now using `from src ...`) — **done**.
- Ensure all entrypoints call `setup_logging(...)` — **done**.
