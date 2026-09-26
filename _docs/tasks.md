# Weekly Project Feedback SaaS — Task Backlog

Derived from [Weekly Project Feedback SaaS — MVP Scope](weekly-project-feedback-mvp-scope.md),
[Tech Stack Options](tech-stack-options.md), and
[Architecture](architecture.md) (Option 1: Django + DRF, Postgres, Celery +
Redis, django-allauth).

**Revision note:** This list targets a buildable **first version** of the app, not full
parity with the MVP scope doc. Small related tasks were merged so each item is a
meaningful, self-contained unit of work; anything not needed to prove the core product
loop (Invite → Submit → Group → Review → Vote → Discuss → Act → Follow up) was pushed to
[§2 Deferred](#2-deferred--post-v1) rather than built now. Nothing deferred is dropped —
it's scoped out of v1, not out of the product.

Each task is small enough for one session and described with enough context to hand off
without reading the others.

---

## 1. In scope for v1

### 1. Empty project with a passing test
Goal: Establish a working project skeleton with a green test suite.
Description: Set up the Django project structure, dependency management, and test runner (pytest or Django's test runner). Add one trivial test (e.g., a health-check view or a smoke test) and confirm it passes before any real feature work begins.

### 2. Tenancy data model: organizations, projects, workstreams, memberships & roles
Goal: Model the full tenancy hierarchy and who belongs to it.
Description: Create the Organization, Project, and Workstream models (Organization → Project → Workstream) plus the Membership model linking a user to any of the three with one of the five roles (platform administrator, organization administrator, project owner, workstream facilitator, project member). A person may hold memberships across multiple organizations, projects, and workstreams at once. No permission enforcement yet — data model only.

### 3. Role-based permission checks
Goal: Enforce the permissions table from the spec at the code level.
Description: Implement a permission-checking layer (e.g., Django permission classes or a custom decorator) mapping each of the five roles to its allowed actions, per the roles/permissions table in the spec. Covers the enforcement mechanism only, not every individual check used by later features.

### 4. Auth: email and password
Goal: Let a user sign up and log in with email and password.
Description: Implement standard email/password registration and login using django-allauth, covering signup, login, logout, and password reset. No OAuth or magic-link support in this task.

### 5. Auth: passwordless email link
Goal: Let a user log in via a one-time emailed link instead of a password.
Description: Add "magic link" login: a user requests a link by email, receives a time-limited single-use token, and is logged in when they click it. The token must expire and be invalidated after use.

### 6. Auth: social login (Google & Microsoft)
Goal: Let a user authenticate using a Google or Microsoft account.
Description: Integrate both Google and Microsoft OAuth as login/signup methods via django-allauth's social providers, linking each identity to a user account (creating one if needed). Both providers follow the same allauth pattern, so they're implemented together.

### 7. Organization creation & administration
Goal: Let a user create an organization and manage its administrators.
Description: Build self-serve organization creation (the creator becomes its first organization administrator) plus the ability for an organization administrator to appoint additional org administrators within the same organization. (Manual platform-admin approval of new organizations is deferred — see §2.)

### 8. Invitations: create, resend, expire, revoke
Goal: Let owners/admins invite people into a project or workstream by email.
Description: Implement invitations tied to an email address, organization, project, workstream, and role, with a 14-day expiry and the ability to resend or revoke a pending invitation.

### 9. Invitation acceptance, guest scoping & participant removal
Goal: Turn an accepted invitation into access, and let access be revoked cleanly.
Description: Build the acceptance flow that turns a valid invitation into an active Membership (rejecting acceptance from a different email address than the one invited), scope invited "guest" users to only what they were invited to (no organization directory browsing), and implement participant removal that immediately revokes access and voting rights while preserving historical contributions.

### 10. Feedback cycle model, state machine & cadence configuration
Goal: Represent a feedback cycle's lifecycle and how often cycles occur.
Description: Create the FeedbackCycle model scoped to a workstream with the eight lifecycle states (Scheduled, Open, Closed, AI review, Voting, Retrospective, Completed, Archived) and their allowed transitions, plus per-project configuration of feedback cadence (default weekly), retrospective cadence (default biweekly, covering the two preceding cycles), and the project's time zone for deadlines and reminders.

### 11. Weekly feedback form and submission
Goal: Let a project member submit the standard weekly feedback form.
Description: Build the form with its five fields (accomplishments, blockers/risks, improvement suggestions, help/decisions needed, and a required five-point confidence score), where written responses are optional and the confidence score is mandatory. Submissions are named by default.

### 12. Per-response anonymity, submission window rules & facilitator-exclusion routing
Goal: Cover the remaining submission-time behaviors on top of the base form.
Description: Add a per-response "Submit anonymously" toggle (with a pre-submission preview of "Submitted as [name]" or "Submitted anonymously"), enforce that contributors can edit or withdraw their own response only while the window is open and cannot view others' responses early, block late submissions unless a facilitator/owner grants a logged extension, and add an "Exclude from facilitator review" option that routes a response to another authorized facilitator or an org admin.

### 13. Anonymous identity protection
Goal: Guarantee anonymous contributors cannot be identified through the system.
Description: Store anonymous-submission identity in a separate, restricted table (not a normal joinable field), so no ordinary query, view, or export can expose it. An internal identity link may be retained for documented security/legal needs, accessible only through a restricted, logged path.

### 14. De-identification pipeline for AI processing
Goal: Strip identity before any content reaches the AI provider.
Description: Build a reusable preprocessing step that removes names, user IDs, email addresses, and other identity metadata from feedback content before it is sent to the AI provider, structured so no future AI call site can bypass it.

### 15. AI theme generation integration
Goal: Generate suggested themes and summaries from a closed cycle's responses.
Description: Integrate with an approved AI provider (contractually non-training on submitted data) to group de-identified responses into suggested themes with draft summaries, duplicate-theme flags, excerpt suggestions, and risk highlights — recording the model, generation time, and a traceable link back to source responses for every draft. Handle provider timeouts/errors/rate limits so a failure marks the cycle "needs manual review" instead of blocking it.

### 16. Facilitator theme review, publication & manual fallback
Goal: Let a facilitator turn AI drafts — or fully manual themes — into published themes.
Description: Build the review screen where a facilitator approves, edits, merges, or rejects each suggested theme, removes identifying details, optionally selects safe excerpts, and publishes the final set (opening voting). The same screen must support creating and editing themes entirely by hand, since it is also the path used when AI is disabled or unavailable. Record every facilitator decision for the audit log.

### 17. Voting: ballots, credit allocation & privacy
Goal: Let each active workstream member cast a private three-credit ballot per retrospective.
Description: Implement one ballot per member per retrospective with three credits, allowing 1–2 credits per theme (never more than 2 on one theme, remainder optional), changeable until the window closes. Votes stay invisible to everyone (including facilitators) while the window is open, and facilitators can never modify a vote. Members active in multiple workstreams get one ballot per applicable workstream.

### 18. Vote ranking, tie-breaks & facilitator overrides
Goal: Turn closed ballots into a ranked result with the documented override paths.
Description: Compute per-theme totals (credits, unique voters, participation percentage) once voting closes, rank by total credits with unique-voter count as tiebreaker, support a facilitator risk-based tiebreak that requires a recorded reason, and support the "Facilitator-added risk" mechanism for adding an urgent low-ranked item to the agenda — clearly labeled and logged as an override.

### 19. Retrospective session: agenda, decisions, completion & reopening
Goal: Run a retrospective end-to-end and support rare, audited reopening.
Description: Assemble the agenda from ranked themes, facilitator-added risks, and any overdue/blocked actions carried over from prior cycles; let the facilitator record decisions and notes per theme and optional attendance (never usable as a performance metric); publish the completed summary to the workstream; and support a reopen action that requires a recorded reason and produces an audit event.

### 20. Action lifecycle: proposal, approval, acceptance & status tracking
Goal: Take an action from proposal through to a tracked outcome.
Description: Build the proposal form (from a retrospective), the facilitator's approve/edit/merge/reject/defer workflow (requiring title, description, scope, owner, due date, source retrospective, and related theme on approval), and the full status lifecycle (Proposed, Awaiting acceptance, Accepted, In progress, Blocked, Completed, Rejected, Cancelled) — including the owner's accept/decline-with-reason step and logging any reassignment.

### 21. Confidence-score aggregation & privacy threshold
Goal: Show confidence trends without ever exposing an individual score.
Description: Implement aggregate confidence scoring per workstream/project with a configurable minimum-response threshold (absolute floor of five), hiding results below threshold with the specified message, and preventing filter combinations that could isolate an individual's score.

### 22. In-app notifications
Goal: Deliver the core notification events inside the product UI.
Description: Implement an in-app notification center covering feedback window opened, submission reminder, voting opened, upcoming retrospective, action assigned, action due/overdue, and new summary published, with per-user read state.

### 23. Email notifications
Goal: Deliver the same notification events via email.
Description: Add email delivery for the same event set as the in-app channel, sent asynchronously via a background job so a slow or failed email send never blocks the triggering action.

### 24. Audit log storage and recording
Goal: Provide the durable, queryable audit trail the spec requires.
Description: Build the audit log storage model and a recording utility, and wire it into the events already produced by prior tasks (role/permission changes, invitation lifecycle, deadline changes, theme approval/edit/merge/publish, voting overrides, retrospective reopening, action lifecycle changes). Anonymous identities must never appear in audit output visible to project participants.

### 25. Feedback deletion (manual, audited)
Goal: Let an organization administrator delete retained feedback, with a clean trail.
Description: Implement organization-administrator-initiated deletion of a stored response (and its directly derived published excerpts) without exposing anonymous identities, recalculating or flagging affected themes, and recording a deletion audit event that does not retain the deleted text.

### 26. Member & facilitator dashboards
Goal: Give members and facilitators a working view of what needs their attention.
Description: Build the member dashboard (open feedback requests, upcoming retrospectives, voting tasks, assigned actions, recent summaries) and the facilitator dashboard (participation rate, responses awaiting review, AI-suggested themes, voting status/results, retrospective agenda, proposed/blocked/overdue actions).

### 27. Project owner & organization admin dashboards
Goal: Give project owners and org admins the oversight views they need.
Description: Build the project owner dashboard (workstream participation, approved summaries, confidence trends, escalated risks, project-level actions) and the organization administrator dashboard (members/invitations, projects and roles, retention/threshold settings, integration status, recent audit activity).

### 28. Access control audit: tenant isolation & visibility rules
Goal: Verify strict data separation and the who-sees-what table across all built features.
Description: Review every query path built so far for organization-scoping, add automated tests asserting a user in one organization can never read or mutate another's data through any endpoint, and audit the visibility-model table from the spec (e.g., raw responses visible only to the authorized facilitator, anonymous identity visible to no one) across existing features, closing any gaps found.

### 29. Security baseline: rate limiting, session revocation & secrets handling
Goal: Close out the core security baseline before calling this a v1.
Description: Implement rate limiting/abuse protection on authentication and invitation endpoints, on-demand session revocation, confirm secrets are stored outside application source, and verify no sensitive feedback text reaches application logs or third-party payloads.

### 30. Accessibility pass (WCAG 2.1 AA)
Goal: Bring the built UI up to the spec's accessibility target.
Description: Audit the screens built in prior tasks (forms, dashboards, voting, retrospective) against WCAG 2.1 AA criteria (keyboard navigation, color contrast, screen-reader labeling) and fix identified gaps, across supported desktop/tablet/mobile widths.

---

## 2. Deferred / post-v1

Everything below is in the original MVP scope doc and stays part of the product vision —
it's sequenced after v1 because it either depends on the core loop already working, or
isn't needed to prove the loop end-to-end.

| Item | Why it's deferred |
|---|---|
| Manual platform-admin approval of new organizations | Anti-abuse/governance control, not needed to demo the product loop; v1 uses self-serve org creation instead. |
| Project-level consolidation for >100-member projects | Depends on multiple completed workstream cycles already existing; build once the single-workstream loop is proven. |
| External action-tracker linking (Jira/Asana) | Native in-app action tracking already proves the action-follow-through loop. |
| Slack notifications | Extra integration surface (OAuth app, webhook config); in-app + email already cover "tell the user to act." |
| Microsoft Teams notifications | Same reasoning as Slack. |
| Notification preferences, quiet hours & delivery consolidation | Polish on top of already-working delivery channels. |
| Organization closure & 30-day recovery window | Account-lifecycle edge case, not needed to demo the product loop. |
| History search, filtering & exports (approved summaries/actions) | Reporting convenience; basic browsing is covered by the dashboards in v1. |
| Audited raw-response export workflow | Advanced governance feature that depends on the exports feature above existing first. |
| Moderation flagging for sensitive content | Safety-net layered on top of an already-working publish flow. |
| Restricted platform-security identity-access process | Rare-investigation workflow; not needed until there's real anonymous production data at stake. |
| Periodic retention reminders to admins | Nudge/polish on top of the core deletion capability already in v1. |
