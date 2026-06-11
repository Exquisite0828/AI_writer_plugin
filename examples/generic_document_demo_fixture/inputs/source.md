# Accounts Data Store Migration Source Notes

Project: Accounts Data Store Migration.

The current accounts data service stores customer account settings in the legacy datastore. The migration option under review is a managed PostgreSQL cluster owned by the platform data team.

Confirmed source facts:

- The target readers are engineering leadership and the platform data team.
- The preferred maintenance window is Sunday 02:00 UTC to 04:00 UTC.
- The current downtime target is no more than 30 minutes during the migration window.
- The rollback approach is documented as draft only.
- The cost model has not been reviewed by finance.
- The compliance review has not been completed.
- No owner has recorded the final migration decision.
- The monitoring plan includes database latency, replication delay, and application error-rate dashboards.
- The source material does not provide final cutover approval.

Open source gaps:

- Finance must confirm the cost model.
- Compliance must confirm data retention handling.
- Engineering leadership must confirm the final decision.
- Operations must confirm the rollback procedure.
