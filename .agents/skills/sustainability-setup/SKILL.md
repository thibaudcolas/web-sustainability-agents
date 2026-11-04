---
name: sustainability-setup
description: Prepare the runtime and choose a representative public-site audit scope from a URL, owner priorities and optional source context. Use before collecting a sustainability audit.
license: MIT
metadata:
  version: "0.2.0"
---

# Setup and sampling

Own prerequisites and sampling, not the final audit. Return an editable plan and a concise scope summary to the coordinator. Use its supplied output directory and tool root. Run the CLI's `doctor`, then `prepare` if dependencies are missing; install only the declared runtime/browser requirements. If the host lacks uv, Node.js or required browser libraries, report the concrete blocker. Do not ask the owner to run commands the agent can run itself.

Default to 5–10 public pages, including the homepage. Discover relevant pages from navigation, a bounded sitemap and the owner's tasks. Prefer different templates and functions: article/content detail, listing/search, a media-rich page, contact or another key task, and relevant sustainability/privacy information. A count of ten near-identical articles is weaker than five varied pages. Record why each page was selected and what was omitted. Use fewer pages when the owner asks, the site is smaller or access is constrained; explain the exception. Do not invent URLs to meet the count.

Reuse the owner's stated priorities and access boundaries. Ask the coordinator for a question only when the answer materially changes the work. Public exploration can continue while optional preferences are pending. Restricted or mutating flows remain outside scope without authorization. Record assumptions separately from owner answers.

Create the plan with `tool workflow init`, then refine it. Each page needs a visitor task. Discover actual cookie controls and record accept/reject actions where available. Include at least one meaningful complete public journey with destination URL, selector and expected text; all supplied postconditions must match. Select specific source files when available, preserving the distinction between local code and deployed behavior. Source roots alone do not select their contents.

Load `context-review` and select relevant qualitative `contextChecks` for new audits. Start with a meaningful public task's access barriers, then consider data collection, content lifecycle, stated goals and governance where relevant. Use the owner's priorities and discovered public evidence to choose additional decision/research checks; explain omissions. Do not require the owner to choose IDs or supply internal code. Prepare attributed public documents or task observations as `contextEvidence` before collection, using the contextual role's record format. Preserve unresolved evidence requests; do not delay a public audit for unavailable optional internal records. Selected contextual checks use the explicitly extended `agent-breadth-v3` rubric; an intentionally context-free plan retains v2.

Return the absolute plan path, selected pages and rationale, omissions, prerequisites status, and unanswered scope questions. Do not claim collection or page performance from exploratory browsing. The coordinator passes the final plan to the collection role.
