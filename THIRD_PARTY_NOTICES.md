# Third-party software in Limit.less

Updated 6 October 2026. Upstream projects remain identifiable and retain their original notices. Limit.less is a separate product; it does not claim authorship of these projects.

## LinkedIn Skills

- Upstream: [sergebulaev/linkedin-skills](https://github.com/sergebulaev/linkedin-skills)
- Revision: `2f00424615b9853e8b1aa003d8752179bbeabb09` (cloned 6 October 2026)
- License: MIT; copyright (c) 2026 Sergey Bulaev.
- Source and complete license: `integrations/linkedin-skills/` and `integrations/linkedin-skills/LICENSE`.
- Limit.less uses its skill references to generate private drafts, its Apify client for opt-in public-post research, and its Publora client for user-approved LinkedIn operations. Draft generation does not publish. Every publish action requires the user to review the exact text and select a channel. Scheduled posts require a future time; comments publish immediately after separate approval. A provider timeout is recorded as uncertain and is never retried automatically.
- No account password, session cookie, or LinkedIn login is requested. Third-party provider API keys are encrypted at rest and excluded from privacy exports.

## ApplyPilot

- Upstream: [Pickle-Pixel/ApplyPilot](https://github.com/Pickle-Pixel/ApplyPilot)
- Revision: `4a8d521f67f5139811c0a910ef37410f8e6d836a` (cloned 6 October 2026)
- License: AGPL-3.0-only; copyright remains with its authors. Complete license: `integrations/ApplyPilot/LICENSE`.
- The unmodified upstream source is included as a separate integration. Its CLI and browser automation are not launched by the Limit.less web service. Applying requires setup and job-by-job review; this workspace's Greenhouse workflow prepares an evidence packet and hands off to the employer form. That flow does not submit applications.
- Operators who deploy or modify ApplyPilot must review and meet the AGPL's applicable source and notice obligations. Limit.less brand assets and surrounding application code do not change the upstream license.

The separate local Gemini worker in `apps/api/app/runtime/automation.py` and `browser_apply.py` is an original implementation. It does not execute or incorporate ApplyPilot code. Its browser and PDF dependencies are Playwright and ReportLab, installed through `requirements-automation.txt`.

## Additional reviewed repositories

- [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops) and [theaayushstha1/job-applier-agent](https://github.com/theaayushstha1/job-applier-agent) informed workflow review. No source from these projects is bundled.
- [ApplyPilot](https://github.com/Pickle-Pixel/ApplyPilot) is listed above because its source is now included.
- The user's [Behance reference](https://www.behance.net/gallery/205093205/AI-Job-Search-Platform-UX-UI-Case) was not accessible to the reader. Supplied screenshots informed the visual direction; the reference's product name, labels and artwork were not copied.
