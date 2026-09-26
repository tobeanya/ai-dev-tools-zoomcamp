# Weekly Project Feedback SaaS — Architecture

**Status:** Draft — for discussion

**Related:**
[MVP Scope](weekly-project-feedback-mvp-scope.md) ·
[Tech Stack Options](tech-stack-options.md) ·
[Task Backlog](../_docs/tasks.md)

**Stack:** Django + Django REST Framework, PostgreSQL, Celery + Redis, django-allauth.

---

## 1. Architectural style

A single Django **monolith**, organized into focused Django apps by domain, backed by one
PostgreSQL database and one Celery worker pool. No microservices: the MVP's scale
(≤1,000 members/project, ≤10,000 feedback entries/cycle) doesn't justify the operational
cost, and the spec's cross-cutting requirements (RBAC, audit logging, tenant isolation,
anonymity) are far easier to enforce consistently inside one codebase and one database
than across service boundaries.

The UI is server-rendered Django templates with HTMX and Alpine.js for interactivity
(partial page updates for voting, form submission, dashboards), rather than a separate
SPA. This is the default recommendation for this project because:

- It avoids a second codebase and a duplicated permissions/serialization layer.
- Most screens (forms, dashboards, review queues) are document-and-list oriented, not
  highly interactive — a good match for HTMX.
- DRF is still used underneath for anything that benefits from a clean JSON contract
  (notification webhooks, potential future mobile/API clients, Slack/Teams integration
  payloads), so the option to add a JS-heavy frontend later isn't closed off.

This is a decision point, not a constraint from the stack choice itself — revisit if the
UI turns out to need heavier client-side state than HTMX comfortably handles.

## 2. System components

```
                          ┌─────────────────────┐
                          │        Users          │
                          │ (browser / Slack /    │
                          │  Teams / email client) │
                          └──────────┬────────────┘
                                     │ HTTPS
                          ┌──────────▼────────────┐
                          │   Django application   │
                          │  (web process, WSGI/    │
                          │   ASGI behind a proxy)  │
                          │                        │
                          │  Templates + HTMX UI   │
                          │  DRF API endpoints     │
                          └───┬───────────┬────────┘
                              │           │
                 enqueue jobs │           │ reads/writes
                              │           │
                    ┌─────────▼───┐   ┌───▼─────────────┐
                    │    Redis     │   │   PostgreSQL     │
                    │ (broker +    │   │ (single DB,      │
                    │  cache)      │   │  org-scoped      │
                    └───┬──────────┘   │  tables, RLS      │
                        │              │  optional)        │
              ┌─────────▼─────────┐   └───────────────────┘
              │  Celery workers    │
              │ (AI calls, email,  │
              │  Slack/Teams push, │
              │  scheduled cycle   │
              │  transitions)      │
              └───┬───────────┬───┘
                  │           │
        ┌─────────▼──┐   ┌────▼─────────────┐
        │ AI provider │   │ Email / Slack /   │
        │ (de-identi- │   │ Teams APIs        │
        │ fied input) │   │                   │
        └─────────────┘   └───────────────────┘

                    ┌───────────────────┐
                    │   Celery beat      │
                    │ (cron-style        │
                    │  scheduler: cycle  │
                    │  opens/closes,     │
                    │  reminders, digest) │
                    └───────────────────┘
```

| Component | Responsibility |
|---|---|
| Django web process | Request/response handling, auth, permission checks, template rendering, DRF endpoints, enqueues Celery jobs, never calls the AI provider or notification APIs synchronously |
| PostgreSQL | System of record for all tenants; every tenant-scoped table carries an organization (and usually project/workstream) foreign key |
| Redis | Celery broker/result backend and general-purpose cache (rate limiting counters, session data if needed) |
| Celery workers | All slow or unreliable I/O: AI theme generation, outbound email/Slack/Teams delivery with retry, export generation, deletion/retention sweeps |
| Celery beat | Time-based triggers: opening/closing feedback windows, sending reminders, escalating overdue actions, retention reminders |
| AI provider | Called only with de-identified content, only from a worker process, never from the request/response cycle |

## 3. Django app boundaries

Each app owns its own models, migrations, and business logic, and maps roughly to a
section of the MVP scope. This grouping is a starting point — the aim is to keep each
app small enough that a task from the [backlog](../_docs/tasks.md) usually touches one or
two apps, not all of them.

| App | Owns |
|---|---|
| `accounts` | User model, django-allauth integration (password, magic link, Google, Microsoft), session/security settings |
| `tenancy` | Organization, Project, Workstream, Membership, roles, invitations |
| `permissions` | Shared RBAC enforcement (permission classes/mixins used by every other app) — no models of its own |
| `feedback` | FeedbackCycle state machine, weekly feedback form, submissions, anonymity handling, submission-window rules |
| `themes` | De-identification pipeline, AI provider integration, AI failure/fallback handling, facilitator theme review and publication |
| `voting` | Ballots, credit allocation, ranking, tie-breaks, facilitator overrides |
| `retrospectives` | Agenda assembly, session notes/decisions, completion, reopening |
| `actions` | Action proposals, approval, status lifecycle, external-tracker linking |
| `consolidation` | Cross-workstream and project-level summary rollups |
| `notifications` | Channel abstraction (in-app, email, Slack, Teams), user preferences, delivery retry/consolidation |
| `audit` | Audit log storage and the recording utility used by every other app |
| `retention` | Deletion workflows, retention reminders, organization closure/recovery window |
| `exports` | Approved-summary exports, audited raw-response export workflow |
| `moderation` | Flagging, withholding flagged content pending review |
| `dashboards` | Read-only aggregation views per role (member, facilitator, project owner, org admin) — depends on the apps above but shouldn't be depended on by them |

Dependency direction is intentionally one-way where possible: `permissions` and `audit`
are used by nearly everything and depend on nothing domain-specific; `dashboards` depends
on everything and nothing depends on it.

## 4. Data model overview

Core tenancy and workflow entities, at the level of detail needed to reason about
architecture (not a full schema):

- **Organization** → **Project** → **Workstream** is the tenancy spine. Every
  tenant-scoped model carries at least an `organization_id`, and usually a
  `project_id`/`workstream_id`, even if it could be derived transitively — this keeps
  tenant-isolation queries and checks simple and hard to get wrong.
- **Membership** links a `User` to an Organization, Project, or Workstream with a role.
  A user can hold multiple memberships across multiple tenants.
- **Invitation** is a separate model from Membership (pending vs. active), with its own
  expiry and revocation state.
- **FeedbackCycle** belongs to a Workstream and holds the 8-state lifecycle. **Response**
  belongs to a FeedbackCycle and, when anonymous, stores no identity foreign key visible
  to normal queries (see §6).
- **Theme** belongs to a FeedbackCycle (or, for consolidation, to a Project), with a
  traceability link to the Responses it was built from, and provenance fields (model
  used, generation timestamp, generated-vs-edited state).
- **Ballot** and **Vote** belong to a member and a retrospective; results are computed,
  not stored as a running tally, so privacy-during-voting is a query-time property, not
  something that needs separate access control on write.
- **Retrospective** belongs to a Workstream and aggregates published Themes, Votes,
  decisions, and Actions for a given cycle pairing.
- **Action** belongs to a Workstream or Project, with an owner, status, and links back to
  its source Retrospective and Theme.
- **AuditEvent** is append-only and references the acting user, the affected entity, and
  a redacted description — never the anonymous-identity link.
- **NotificationPreference** and **NotificationDelivery** are separate from the
  triggering entities, so delivery retries and channel preferences don't leak into
  domain models.

## 5. Multi-tenant isolation

- **Isolation strategy:** shared database, shared schema, with mandatory
  organization-scoping on every tenant-scoped query. This is simpler to operate than
  schema-per-tenant or database-per-tenant at this scale, and easier to back up/restore
  atomically.
- **Enforcement:** a base queryset manager/mixin used by every tenant-scoped model
  requires an explicit organization (or project/workstream) filter; there is no
  "unscoped" query path in normal application code. Row-level security in Postgres is a
  defense-in-depth option worth adding once the ORM-level scoping is stable, but it is
  not a substitute for it — application code still needs to reason about scope
  explicitly for the permission model to make sense.
- **Verification:** cross-tenant access is covered by automated tests that assert a user
  in Org A can never read or mutate Org B's data through any endpoint, not just the ones
  where isolation is "obviously" needed (backlog task 54).

## 6. Anonymity architecture

Anonymity is the highest-stakes property in the system, so it's treated as a first-class
architectural concern rather than a field-level flag:

- An anonymous Response stores contributor identity in a **separate, restricted table**
  (not a nullable foreign key on the Response itself), so a normal join or serializer
  cannot accidentally expose it. Only the restricted platform-security access path
  (backlog task 49) queries that table, and every such query is itself an audited event.
- The **de-identification pipeline** (backlog task 21) is the only code path allowed to
  construct the payload sent to the AI provider. It is enforced structurally: the AI
  client module only accepts its own de-identified value type, not a raw Response, so a
  future call site cannot bypass de-identification by construction.
- Anonymous identity never appears in: AI provider payloads, published themes/excerpts,
  notification payloads (Slack/Teams/email), exports, or application logs. This is
  covered by the same de-identification boundary plus a log-scrubbing convention
  (structured logging with an explicit denylist of fields, not string interpolation of
  model objects).

## 7. RBAC and permissions

- Roles are attached to a Membership, not globally to a User — the same user can be a
  facilitator in one workstream and an ordinary member in another.
- Permission checks are centralized in the `permissions` app as reusable
  checks/decorators (e.g., "can approve themes in this workstream") rather than scattered
  role-string comparisons in views. Every view and DRF viewset goes through one of these
  checks; there is no endpoint that infers permission from the request payload alone.
- The roles/permissions table in the MVP scope is the source of truth; the `permissions`
  app is a direct implementation of that table, not a superset of it — new permissions
  require a spec update first.

## 8. Workflow state machines

- **FeedbackCycle** (8 states) and **Action** (8 statuses) are modeled as explicit state
  machines (e.g., via `django-fsm` or an equivalent constrained-transition approach)
  rather than a free-text status field. Invalid transitions (e.g., publishing a theme on
  a cycle that isn't in "AI review") are rejected at the model layer, not just the UI
  layer.
- Time-based transitions (cycle opens/closes, voting window closes) are driven by Celery
  beat, not by a request happening to arrive at the right time — a cycle closes on
  schedule even if no user is actively using the product at that moment.
- Every transition that the spec requires to be audited (deadline extension, retro
  reopening, voting override) calls into the `audit` app synchronously, in the same
  transaction as the transition — audit and state change never get out of sync.

## 9. AI integration architecture

- **Provider abstraction:** a thin internal interface wraps the actual AI provider SDK,
  so the provider can be swapped (or disabled entirely) without touching calling code in
  `themes`.
- **Execution:** AI calls happen only inside Celery tasks, never inline in a request.
  Timeouts, rate limits, and provider errors are caught at the task level and surfaced as
  a "needs manual review" state on the affected cycle rather than a failed request the
  user sees.
- **Kill switch:** an organization-level flag disables AI entirely; when disabled, the
  `themes` app's manual creation/merge/edit path is the only path exercised, and it is
  the same UI facilitators use to correct AI output — no separate "manual mode" screens
  to maintain.
- **Auditability:** every AI-generated draft records the model identifier and generation
  timestamp, and is immutable once generated — facilitator edits produce a new
  publication record rather than overwriting the AI draft, preserving traceability from
  a published theme back to both the AI output and the source responses.

## 10. Notifications architecture

- A single internal `Notification` concept with channel-specific delivery adapters
  (in-app, email, Slack, Teams) behind one interface, so new event types don't need to
  know about channel-specific mechanics, and a new channel doesn't need to touch every
  event's triggering code.
- Delivery happens via Celery tasks with retry/backoff; failures beyond the retry budget
  are surfaced to organization administrators (per spec) rather than silently dropped.
- Slack/Teams adapters only ever construct payloads from the same de-identified,
  already-published data the in-app/email channels use — there is no separate code path
  that could accidentally include anonymous response text.
- User-level preferences (channel choice, quiet hours, reminder frequency) are read at
  delivery time by the adapter layer, and duplicate-notification consolidation happens
  before tasks are enqueued, not after delivery.

## 11. Audit logging

- `AuditEvent` is append-only (no update/delete in normal application code) and captures:
  actor, action type, affected entity reference, timestamp, and a redacted
  human-readable description.
- Writing an audit event is a first-class part of the business operation it describes
  (same DB transaction), not a side effect bolted on via signals — this avoids the
  failure mode where an action succeeds but its audit trail silently doesn't.
- Audit event descriptions go through the same redaction convention as logs: anonymous
  contributor identity is structurally unavailable to the code path that writes
  human-facing audit descriptions.

## 12. API layer

- DRF is used for: the HTMX partial endpoints that need JSON (rare — most HTMX responses
  are server-rendered HTML fragments), the Slack/Teams inbound/outbound integration
  surface, and any endpoint intended for future external consumption (exports, potential
  mobile client).
- Versioning: a URL-prefixed version (`/api/v1/...`) from day one, even with a single
  consumer, since Slack/Teams webhook contracts are effectively an external API the
  moment they exist.
- Serializers enforce the same permission and tenant-scoping rules as the template views
  by sharing the `permissions` app's checks — there is one authorization implementation,
  not two.

## 13. Deployment topology

Minimum viable production topology, expressed as processes rather than a specific host:

| Process | Purpose | Scaling axis |
|---|---|---|
| `web` | Django app server (Gunicorn/Uvicorn behind a reverse proxy) | Horizontal, stateless |
| `worker` | Celery worker(s) | Horizontal; separate queues for AI calls vs. notification delivery if one starts starving the other |
| `beat` | Celery beat scheduler | Exactly one instance |
| `postgres` | Primary datastore | Vertical first; read replica later only if dashboards become a bottleneck |
| `redis` | Broker + cache | Vertical; not a source of truth, so it can be resized/restarted without data-loss risk to the product |

Local development runs all of these via a single Docker Compose file. Production can be a
managed platform (Render/Fly/Railway/ECS) — the process list above is what any target
needs to support, not a specific vendor choice.

## 14. Configuration and secrets

- Twelve-factor style configuration: all environment-specific values (DB URL, Redis URL,
  AI provider key, OAuth client secrets, Slack/Teams app credentials) come from
  environment variables, never committed to source.
- Per-environment settings modules (`settings/base.py`, `settings/dev.py`,
  `settings/prod.py`) share the base and override only what differs, so environment drift
  is visible in diffs.

## 15. Observability

- **Application logs:** structured (JSON) logging with an explicit denylist for
  anonymous-identity and raw-feedback-text fields, enforced by a shared logging helper
  rather than left to each call site's discipline.
- **Error tracking:** exceptions from both the web process and Celery tasks go to the
  same error-tracking sink, tagged with organization/workstream where available (never
  with anonymous-identity data) to speed up tenant-specific debugging.
- **Audit log vs. application log:** these are deliberately separate systems — the audit
  log is a product feature with retention and access-control requirements of its own; the
  application log is an operational tool and is not a substitute for it.

## 16. Testing strategy

- `pytest-django` with `factory_boy` factories for the core tenancy/membership objects,
  since nearly every test needs an Organization/Project/Workstream/Membership fixture.
- Permission and tenant-isolation tests are treated as a first-class suite, not folded
  into feature tests — they assert the negative case (user X cannot do Y) as often as the
  positive case.
- Celery tasks are tested with eager-mode execution in the test suite plus a small number
  of integration tests against a real Redis in CI to catch serialization issues eager
  mode would hide.

## 17. Open decisions

- Whether Postgres row-level security is added as defense-in-depth on top of ORM-level
  tenant scoping, and when (recommended: after the ORM-level approach is stable, not
  before).
- Whether the frontend stays HTMX/Alpine for the full MVP or a specific screen (e.g., live
  voting results) warrants a small islands-of-React approach.
- Choice of state-machine library (`django-fsm` vs. hand-rolled) — deferred to the task
  that implements the FeedbackCycle model (backlog task 14).
- Specific AI provider — deferred until the provider's contractual no-training guarantee
  and API stability are confirmed (backlog task 22).
