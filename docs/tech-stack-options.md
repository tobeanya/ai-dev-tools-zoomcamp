# Weekly Project Feedback SaaS — Tech Stack Options

**Status:** Decided — Option 1 (Django)

**Related:** [Weekly Project Feedback SaaS — MVP Scope](weekly-project-feedback-mvp-scope.md)

---

## 1. Context

The MVP scope requires: multi-tenant org/project/workstream hierarchy, five-role RBAC,
four auth methods (password, passwordless email, Google, Microsoft), a multi-state
feedback-cycle and action-status workflow, anonymized AI theme generation (de-identified
before leaving the system), credit-based voting, multi-channel notifications (in-app,
email, Slack, Teams), a full audit log, and retention/deletion/export rules — at a modest
scale (≤1,000 members/project, ≤10,000 feedback entries/cycle).

This favors a stack strong on relational data modeling, RBAC, background job processing,
and workflow/state-machine support over one optimized for raw throughput.

## 2. Options comparison

| | **1. Django + DRF (Python)** | **2. Next.js (TypeScript)** | **3. Ruby on Rails** | **4. Supabase/Firebase (BaaS)** |
|---|---|---|---|---|
| **Backend** | Django + Django REST Framework | Next.js (App Router) as API + UI | Rails (API or Hotwire/Turbo) | Supabase/Firebase managed backend |
| **Database** | Postgres (Django ORM) | Postgres (Prisma or Drizzle) | Postgres (ActiveRecord) | Postgres (Supabase) or Firestore |
| **Frontend** | Django templates + HTMX/Alpine, or separate React SPA | React Server Components / client components | Hotwire/Turbo, or separate SPA | Any SPA (React/Next.js/SvelteKit) |
| **Auth** | django-allauth (password, magic link, Google, Microsoft) | Auth.js / NextAuth (all four methods built in) | Devise + OmniAuth + devise-passwordless | Built-in auth (email, magic link, Google, Microsoft) |
| **Background jobs** | Celery + Redis | BullMQ + Redis, or Inngest/Trigger.dev | Sidekiq + Redis | Serverless/Edge Functions + cron triggers |
| **RBAC** | Django permissions framework | Custom, enforced in app code / DB policies | Pundit or CanCanCan | Row-level security (RLS) policies |
| **State machines** (cycle states, action statuses) | Built via model methods/FSM libs; Celery for transitions | Manual implementation | AASM gem — strong fit | Hand-built in functions; fights BaaS model |
| **Audit logging** | Custom or django-simple-history | Custom | paper_trail gem — strong fit | Custom, split across RLS + functions |
| **AI integration** | Server-side call from Celery task; easy to enforce de-identification before send | Server-side API route; same enforcement possible | Server-side job; same enforcement possible | Must happen in a function, never client-side — easy to get wrong |
| **Time to first MVP** | Medium | Medium | Medium | Fast |
| **Multi-tenant isolation** | App-level, well-supported by ORM patterns | App-level or Postgres RLS (manual) | App-level, well-supported | RLS-native |
| **Ecosystem fit** | Matches Python-oriented course context; strong AI/ML tooling | Single language across stack; large hiring pool | Convention-heavy, good for CRUD/workflow apps | Fastest to prototype, weakest fit for complex workflow/audit needs |

## 3. Pros, cons, and risks

### Option 1: Django + DRF (Python)

- **Pro:** RBAC, admin tooling, and async jobs (Celery) come largely built in, reducing custom code for the permission model and audit trail.
- **Con:** If a rich SPA UI is needed for the multiple role-specific dashboards, you end up maintaining Django (API) and a separate frontend as two codebases.
- **Risk:** Celery/Redis is another moving part to operate (broker, workers, monitoring); AI-call failures or Slack/Teams delivery failures must be handled explicitly in task retry logic or reminders and notifications silently stop firing.

### Option 2: Next.js (TypeScript)

- **Pro:** One language end-to-end lowers context-switching and hiring friction; React Server Components suit the several distinct dashboards well.
- **Con:** No built-in RBAC, state-machine, or audit-log framework — the 8-state feedback cycle, 8-state action lifecycle, and audit requirements are all hand-rolled.
- **Risk:** Background job reliability (AI theme generation, notification retries, scheduled reminders/deadline transitions) depends on a bolted-on queue (BullMQ/Inngest); if retry/backoff logic is incomplete, the spec's "handle provider errors without blocking the retrospective" requirement can silently fail.

### Option 3: Ruby on Rails

- **Pro:** AASM (state machines) and paper_trail (audit log) are mature, well-tested gems that map almost directly onto the cycle-state and audit requirements — less custom code than either Option 1 or 2 for this specific spec.
- **Con:** Smaller in-house AI/ML ecosystem than Python; any de-identification or NLP preprocessing before the LLM call is more likely to be a thin wrapper around an external API than something you can build in-process.
- **Risk:** Team/hiring familiarity is usually the limiting factor — Rails talent pools are smaller than Python or JS/TS in most markets, which matters more for a multi-person or long-lived project than a solo MVP.

### Option 4: Supabase/Firebase (BaaS)

- **Pro:** Auth (all four methods), Postgres, and row-level tenant isolation are provided out of the box, giving the fastest path to a working prototype.
- **Con:** The stateful workflows (cycle states, voting windows, retrospective reopening with a recorded reason) don't map cleanly onto a CRUD-first BaaS model, so you end up hand-building a real backend inside serverless functions anyway — eroding the initial speed advantage as the app grows.
- **Risk:** The anonymity guarantee is the highest-stakes requirement in the spec (no participant, facilitator, or owner may ever identify an anonymous contributor, and identity must never reach the AI provider). In this architecture that logic is split between RLS policies and client/function code — a misconfigured policy or a function that forwards a user ID by mistake breaks anonymity in a way that's hard to detect and worse to explain after the fact.

## 4. Recommendation

Options 1–3 share the same shape (monolith + relational DB + background job queue) and
differ mainly by language/ecosystem and how much is "built in" for RBAC, state machines,
and audit trails. Option 4 trades long-term architectural fit for short-term speed, which
is risky given how central anonymity-preservation and the multi-step workflow states are
to this spec.

Given the AI safeguards (de-identify before sending to a provider, never on the client,
full audit trail, graceful degradation when AI is unavailable) and workflow-state
complexity, **Option 1 (Django) or Option 2 (Next.js)** are the strongest fits — both keep
that logic server-side and auditable. Option 1 provides more "for free" (RBAC, admin,
async jobs) for teams comfortable in Python; Option 2 keeps the stack to one language.

## 5. Decision

**Chosen: Option 1 — Django + DRF (Python), Postgres, Celery + Redis, django-allauth.**

No implementation started yet.
