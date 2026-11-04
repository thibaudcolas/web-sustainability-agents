# Maintain and publish skills

The [skill catalog](../agent-skills.md) describes the audit roles. For installation and invocation, use [the audit guide](../using/README.md). This page is for contributors changing the shared skill sources and documentation catalogs.

## Published discovery resources

The build publishes complete skill folders and two discovery catalogs relative to the site's base URL:

- `.well-known/agent-skills/<name>/SKILL.md` and its supporting files.
- `.well-known/agent-skills/index.json`: descriptions, URLs and SHA-256 digests following the [Agent Skills discovery proposal](https://github.com/cloudflare/agent-skills-discovery-rfc).
- `.well-known/ai-catalog.json`: publisher, versions and absolute URLs following [AI Catalog](https://ai-catalog.io/).

Keep the project-site prefix before `.well-known/`. These resources require a compatible discovery client and do not install the collector runtime or create a plugin package.

## Edit a skill

Create `.agents/skills/<name>/SKILL.md` with YAML front matter:

```yaml
---
name: my-skill
description: Describe the task this skill supports and when an agent should use it.
metadata:
  version: "1.0.0"
---
```

Use lowercase letters, digits, and single hyphens for the name, matching the directory name. Add the instructions below the front matter. Keep supporting references, scripts, and assets inside the skill folder: the build copies the whole folder. Symlinks are rejected. Every skill in this directory is published, so keep local-only material elsewhere.

Update `metadata.version` when releasing changes to the skill. Catalog versions come from skill metadata, independently of the workspace version. The catalog omits optional modification dates rather than reporting checkout time as a content update.

Run `just build-docs` and inspect `site/.well-known/`. Invalid metadata fails the build. The publishing hook in `scripts/publish_skills.py` generates catalogs from the skills and the `site_name` and `site_url` settings in `mkdocs.yml`. Update those settings when adopting this template. An empty skills directory produces empty catalogs.

GitHub Actions includes hidden files in its Pages artifact so `.well-known/` is deployed with the documentation. Publishing uses the existing deployment on pushes to `main`; no separate release or package upload is needed.
