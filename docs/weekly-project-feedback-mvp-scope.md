# Weekly Project Feedback SaaS

## Minimum Viable Product Scope

**Version:** 1.0

**Status:** Finalized

**Date:** September 25, 2026

---

## 1. Product summary

The product is a multi-tenant SaaS platform for large project teams. It collects structured weekly feedback from every team member, protects optional anonymity, converts high-volume feedback into reviewable themes, guides workstream retrospectives, consolidates results into project-level summaries, and tracks resulting actions.

The product is a feedback, retrospective, and continuous-improvement system. It is not a replacement for a full project-management platform.

### Core product loop

> Invite → Submit → Group → Review → Vote → Discuss → Act → Follow up

## 2. Product goals

The MVP must enable organizations to:

- Collect useful weekly feedback from every project participant.
- Surface accomplishments, blockers, risks, decisions needed, and improvement opportunities.
- Allow each response to be submitted with the contributor's name or anonymously.
- Give every eligible member an equal opportunity to prioritize discussion topics.
- Turn large volumes of written feedback into facilitator-reviewed themes.
- Run biweekly workstream retrospectives and create a consolidated project summary.
- Convert agreed improvements into owned, trackable actions.
- Show project confidence trends without exposing individual responses.
- Support projects containing more than 100 participants.

## 3. Target customers and supported scale

### Target customers

- Organizations running large, cross-functional projects.
- Projects divided into workstreams or subteams.
- Project participants who may include employees, contractors, clients, and invited external contributors.

### MVP tested limits

- Up to 1,000 members per project.
- Up to 100 workstreams per project.
- Up to 10,000 feedback entries per cycle.

Deployments above these limits are not guaranteed during the MVP.

## 4. Product hierarchy

```text
Organization
└── Project
    ├── Workstreams
    │   ├── Members
    │   ├── Weekly feedback cycles
    │   ├── Themes and voting
    │   ├── Retrospectives
    │   └── Workstream actions
    ├── Project-wide summary
    └── Project-wide actions
```

A person may belong to multiple organizations, projects, and workstreams.

## 5. Roles and permissions

| Role | Core permissions |
|---|---|
| Platform administrator | Approves initial organization administrators and handles authorized platform-level security and abuse matters. |
| Organization administrator | Configures the organization, administrators, retention, privacy thresholds, integrations, projects, and audit access. |
| Project owner | Configures a project, creates workstreams, invites participants, appoints facilitators, and oversees project summaries. |
| Workstream facilitator | Reviews responses, approves AI themes, manages voting and agendas, conducts retrospectives, and approves actions. |
| Project member | Submits feedback, votes, participates in retrospectives, proposes actions, and manages assigned actions. |

The project owner is the default facilitator but may appoint another active project member as facilitator for a workstream or retrospective.

Neither project owners nor facilitators can identify anonymous contributors.

## 6. Organization creation, authentication, and invitations

### Organization creation

- Only approved organization administrators may create organizations.
- A platform administrator manually approves the first administrator for an organization.
- The first organization administrator may appoint additional organization administrators.

### Supported authentication

- Email and password.
- Passwordless email link.
- Google account.
- Microsoft account.

Enterprise SSO is outside the MVP.

### Invitations

- Anyone with a valid project invitation may participate.
- Invitations are tied to an email address, organization, project, workstream, and role.
- Invitations expire after 14 days and may be resent.
- Owners and administrators may revoke pending invitations.
- A forwarded invitation cannot be accepted using a different email address.
- Guests see only the projects and workstreams to which they were invited.
- Guests cannot browse the wider organization directory.
- Removing a participant immediately removes access and future voting rights.
- Historical contributions remain subject to the organization's retention policy.

## 7. Feedback cycles

### Default cadence

- Feedback collection occurs weekly.
- Workstream retrospectives occur every two weeks.
- Each retrospective normally covers the two preceding feedback cycles.
- Organization or project administrators may configure both schedules.
- Every project has a designated time zone used for deadlines, reminders, and meeting times.

### Cycle states

1. Scheduled
2. Open
3. Closed
4. AI review
5. Voting
6. Retrospective
7. Completed
8. Archived

### Submission rules

- Contributors cannot view other responses before the submission window closes.
- Contributors may edit or withdraw their own responses while the window is open.
- Late submissions are blocked by default.
- The project owner or facilitator may extend a deadline; the extension is logged.
- After a cycle closes, removal follows the formal deletion process.

## 8. Weekly feedback form

Every weekly form includes:

1. Accomplishments and wins.
2. Blockers and risks.
3. What should improve.
4. Help or decisions needed.
5. Team confidence score.

### Form behavior

- The confidence score is required.
- Written responses are optional to avoid forced, low-quality answers.
- Each written response can independently be named or anonymous.
- Named submission is the default.
- A clearly visible **Submit anonymously** control is available for every written response.
- The interface previews either **Submitted as [name]** or **Submitted anonymously** before final submission.

### Confidence question

> How confident are you that this project or workstream is on track this week?

The response uses a five-point scale from **Very low** to **Very high**.

## 9. Anonymity and psychological safety

For an anonymous response:

- Teammates cannot identify the contributor.
- Facilitators cannot identify the contributor.
- Project owners cannot identify the contributor.
- Published themes, summaries, notifications, exports, and excerpts contain no identity metadata.
- Anonymous identities are never sent to the AI provider.
- The system may retain a protected internal identity relationship for documented security, abuse, or legal needs.
- Only authorized platform security personnel may access that relationship.
- Every such access is logged and disclosed in the product's anonymity explanation.

The retrospective interface must reinforce these working rules:

- Discuss the issue, not the presumed author.
- Do not ask an anonymous author to identify themselves.
- Do not retaliate against critical feedback.
- Convert feedback into decisions or clearly documented deferrals.

If a response concerns the assigned facilitator, the contributor may select **Exclude from facilitator review**. The response is routed to another authorized facilitator or, if none exists, an organization administrator.

## 10. Visibility model

| Information | Visibility |
|---|---|
| Contributor's own submission | Contributor |
| Original workstream responses | Authorized workstream facilitator |
| Anonymous contributor identity | No project participant |
| Approved workstream themes | Workstream members |
| Approved representative excerpts | Workstream members |
| Project-level themes and trends | All project members |
| Approved project actions | All project members |
| Escalated risks | Project owner and appropriate facilitator |

Project owners do not routinely receive every original workstream response.

## 11. AI-assisted theme generation

The AI may:

- Group related responses into suggested themes.
- Draft a summary for each theme.
- Identify possible duplicate themes.
- Suggest representative excerpts.
- Highlight potential project-level risks.
- Flag details that may expose an anonymous contributor.

The facilitator must approve, edit, merge, or reject every AI-generated theme before publication.

### AI safeguards

- Use an approved provider that contractually does not train models on submitted data.
- Strip names, user IDs, email addresses, and identity metadata before processing.
- Encrypt data in transit and at rest.
- Never publish AI-generated content automatically.
- Never evaluate individual employee performance.
- Never identify or speculate about anonymous contributors.
- Never produce automated disciplinary recommendations.
- Record the model and generation time for each draft summary.
- Maintain traceability from an approved theme to its authorized source responses.
- Allow organization administrators to disable AI.
- Provide complete manual theme creation, merging, and editing when AI is disabled or unavailable.
- Handle provider errors, timeouts, and rate limits without blocking the retrospective.

## 12. Theme review and publication

After a feedback window closes:

1. AI suggests themes and draft summaries.
2. The facilitator reviews the suggestions.
3. The facilitator corrects inaccurate groupings.
4. The facilitator removes identifying details.
5. The facilitator selects safe representative excerpts when useful.
6. Approved themes are published to the workstream.
7. Voting opens.

Facilitator changes and publication decisions are recorded in the audit log.

## 13. Voting

### Voting model

The MVP uses three-credit dot voting:

- Every active workstream member receives one ballot per retrospective.
- Each ballot contains three voting credits.
- A member may assign one or two credits to a theme.
- No more than two credits may be assigned to the same theme.
- The remaining credit may be assigned to another theme or left unused.
- Voting is optional; members are not forced to use all credits.
- Members may change their votes until the voting window closes.
- Voting is private while the window is open.
- Results appear only after voting closes.
- Facilitators cannot modify votes.
- AI does not vote or determine the final ranking.
- Members active in multiple workstreams receive one ballot in each applicable workstream.

### Ranking and results

Each theme displays:

- Total voting credits.
- Number of unique voters.
- Percentage of participating voters who supported it.

Themes are ranked primarily by total credits. Ties are resolved by unique-voter count. If a tie remains, the facilitator may prioritize the theme with greater project risk and must record the reason.

A facilitator may add an urgent low-ranked risk to the agenda. It must be labeled **Facilitator-added risk** and must not be presented as a voting result. The override is logged.

## 14. Retrospective workflow

1. The feedback window closes.
2. AI suggests themes or the facilitator creates them manually.
3. The facilitator approves the themes.
4. Workstream members vote.
5. Voting closes and results are published.
6. The facilitator prepares the agenda from ranked themes and urgent risks.
7. The team discusses the selected themes.
8. The facilitator records decisions and notes.
9. Members propose improvement actions.
10. The facilitator approves, merges, rejects, or defers proposals.
11. Approved actions receive an owner and due date.
12. The facilitator completes and publishes the retrospective summary.
13. Workstream summaries feed the project-level summary.
14. The next retrospective begins by reviewing outstanding actions.

Attendance tracking is optional and cannot be used as an employee-performance score.

A completed retrospective may be reopened only with a recorded reason and audit event.

## 15. Project-level consolidation

For projects with more than 100 members:

- Feedback, voting, and retrospectives occur within workstreams.
- Facilitators publish approved workstream summaries.
- AI may suggest cross-workstream themes from approved summaries.
- Project owners review the consolidated project-level draft.
- All project members see the approved project summary, trends, decisions, and project actions.
- The project-wide view does not display a single unfiltered list of all raw responses.

## 16. Action management

### Creation and approval

- Any project member may propose an action.
- The facilitator may approve, edit, merge, reject, or defer it.
- An approved action requires a title, description, workstream or project, owner, due date, status, source retrospective, and related theme.
- The proposed owner must accept or decline the assignment.
- Declining requires a short reason.
- Reassignment is logged.

### Action statuses

- Proposed
- Awaiting acceptance
- Accepted
- In progress
- Blocked
- Completed
- Rejected
- Cancelled

Overdue and blocked actions appear at the next retrospective.

### Organization-selected action mode

**Native mode:** Actions are managed inside the product.

**External mode:** Actions contain links to external tools such as Jira or Asana. The MVP supports links and simple exports only. Status is updated manually.

Automatic two-way synchronization is outside the MVP.

## 17. Notifications

Organizations may enable:

- In-app notifications.
- Email reminders.
- Slack notifications.
- Microsoft Teams notifications.

Notifications cover:

- Feedback window opened.
- Submission reminder.
- Voting opened.
- Upcoming retrospective.
- Action assigned.
- Action approaching its due date.
- Action overdue.
- New summary published.

### Notification rules

- Slack and Teams are one-way in the MVP.
- Notifications link users back to the authenticated product.
- Slack and Teams messages contain no anonymous response text.
- Users may choose among the channels enabled by their organization.
- Users may configure quiet hours and nonessential reminder frequency.
- Duplicate notifications are consolidated.
- Failed deliveries are retried and surfaced to administrators.

## 18. Confidence-score privacy

- The organization configures the minimum response threshold.
- The platform enforces an absolute minimum of five responses.
- Results remain hidden below the configured threshold.
- The interface displays **Not enough responses to publish this result safely** when necessary.
- Only aggregate scores and trends are shown.
- Individual scores are never exposed.
- Historical results become hidden if later segmentation could isolate individuals.
- Filters cannot be combined in a way that reveals individual responses.
- Participation counts may be displayed, but nonparticipants are not publicly named.

## 19. Retention, deletion, and exports

### Retention

- Original feedback remains stored until manually deleted.
- Projects and workstreams may be archived without deleting history.
- Administrators receive periodic reminders that retained feedback remains subject to organizational data-handling obligations.

### Deletion

- Contributors may withdraw feedback while the feedback window is open.
- Organization administrators may delete retained feedback without seeing anonymous identities.
- Deleting a response removes directly derived published excerpts.
- Affected themes are recalculated or marked as changed.
- Existing decisions and action items are not automatically deleted.
- The deletion audit event does not retain the deleted text.
- Deleted data is removed from active systems promptly and from backups within 30 days.
- Closing an organization uses a 30-day recovery window before permanent removal.

### History and exports

- Users may search and filter completed cycles, themes, summaries, decisions, and actions according to their permissions.
- Filters include project, workstream, date, status, and theme.
- Authorized users may export approved summaries and actions.
- Exports never contain anonymous identity metadata.
- Raw-response exports require an audited organization-administrator workflow.
- Organization administrators may export organizational data before account closure.

## 20. Moderation and sensitive feedback

- Facilitators may flag harassment, threats, personal attacks, or exposed sensitive information.
- Flagged material is withheld from published excerpts until reviewed.
- Flagging does not reveal an anonymous contributor.
- Feedback concerning a facilitator follows the alternate-review route.
- Documented abuse, security, or legal investigations follow the restricted platform-security process.
- Access to protected identity records is exceptional, authorized, logged, and disclosed.

## 21. Dashboards

### Member dashboard

- Open feedback requests.
- Upcoming retrospectives.
- Voting tasks.
- Assigned actions.
- Recent approved summaries.

### Facilitator dashboard

- Participation rate.
- Responses awaiting review.
- AI-suggested themes.
- Voting status and completed results.
- Retrospective agenda.
- Proposed, blocked, and overdue actions.

### Project owner dashboard

- Workstream participation.
- Approved workstream summaries.
- Project confidence trends.
- Cross-workstream themes.
- Escalated risks.
- Project-level actions.

### Organization administrator dashboard

- Members and invitations.
- Projects and roles.
- Retention and confidence-threshold settings.
- Authentication and notification integrations.
- Audit activity.

## 22. Audit requirements

The audit log records:

- Role and permission changes.
- Invitation creation, revocation, and acceptance.
- Feedback-cycle deadline changes.
- Theme approval, editing, merging, and publication.
- Facilitator voting overrides.
- Retrospective reopening.
- Action approval, assignment, reassignment, and status changes.
- Feedback and project deletion.
- Restricted identity-record access.
- Integration and delivery failures affecting workflow.

Audit logs must not reveal anonymous contributor identities to project participants.

## 23. Security, reliability, and accessibility baseline

- Strict separation of data between organizations.
- Role-based authorization on every protected operation.
- Encryption in transit and at rest.
- Secure, expiring invitation and passwordless-login tokens.
- Rate limiting and abuse protection.
- Session revocation.
- Automated backups and tested restoration.
- Secrets stored outside application source code.
- No sensitive feedback in application logs.
- No anonymous response text in third-party analytics or notification payloads.
- Responsive web experience across supported desktop, tablet, and mobile browsers.
- WCAG 2.1 AA accessibility target.

Formal compliance certifications are outside the MVP, but the architecture must not prevent them later.

## 24. Success measures

The MVP measures:

- Weekly feedback participation rate.
- Percentage of feedback submitted before reminders.
- Workstream retrospective completion rate.
- Percentage of AI themes approved without major correction.
- Recurring blockers identified.
- Percentage of approved actions assigned and accepted.
- Action completion rate.
- Average time from feedback submission to action creation.
- Confidence-score trend.
- Member-reported usefulness of retrospectives.

Metrics are reported at workstream and project levels and cannot be repurposed as individual employee-performance scores.

Pilot targets will be established after baseline usage is observed.

## 25. Explicitly outside the MVP

- Native mobile applications.
- Full project planning and task management.
- Time tracking.
- Employee performance or productivity scoring.
- Individual sentiment scoring.
- AI-generated disciplinary recommendations.
- Automatic publication of AI summaries.
- Two-way Jira, Asana, or other task-system synchronization.
- Feedback submission or action management from Slack or Teams.
- Enterprise SSO.
- Cross-organization benchmarking.
- Payroll and HR-system integrations.
- Public feedback forms.
- Automated billing and complex subscription tiers.
- Formal compliance certification.

## 26. MVP acceptance test

The MVP is complete when a project with more than 100 participants can:

1. Create an organization, project, and multiple workstreams.
2. Invite participants securely and assign roles.
3. Schedule recurring weekly feedback cycles.
4. Collect named and anonymous feedback.
5. Protect anonymous identities throughout the project workflow.
6. Generate AI-suggested themes using de-identified content.
7. Let facilitators review and approve themes.
8. Give every eligible member three voting credits with no more than two per theme.
9. Rank themes using credits and unique-voter support.
10. Conduct workstream retrospectives and record decisions.
11. Consolidate workstream outcomes into a project-level summary.
12. Propose, approve, assign, accept, and track actions.
13. Notify users through configured in-app, email, Slack, and Teams channels.
14. Display aggregate confidence trends without exposing individuals.
15. Search, export, archive, and delete data according to permissions and policy.
16. Continue the core retrospective workflow when AI or an external notification provider is unavailable.

---

## Final scope statement

The MVP delivers a complete, psychologically safer feedback-to-action workflow for large project teams while deliberately excluding full project management, employee surveillance, complex enterprise integrations, and automated decision-making. Its defining capabilities are optional anonymity, facilitator-reviewed AI themes, equal member voting, workstream retrospectives, project-level consolidation, and accountable action follow-through.
