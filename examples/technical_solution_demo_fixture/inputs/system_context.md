# System Context

The target system is an internal feature flag rollout service used by backend services to control staged releases.

The system currently exposes a REST API for reading flag states. Backend clients query the service during request handling.

Current known components:
- API service
- configuration storage
- backend client SDK
- audit log exporter

Current constraints:
- The service must preserve existing REST API compatibility for current backend clients.
- The service must keep audit events for flag changes.
- The deployment environment is a Kubernetes-based internal platform.

Current open questions:
- The final architecture decision has not been approved.
- The security boundary has not been confirmed.
- The rollout risk acceptance has not been confirmed.
