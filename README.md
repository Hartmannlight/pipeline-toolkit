# Pipeline toolkit

Shared container build, security and release actions for Hartmannlight projects.
Consumers pin a commit SHA; Renovate updates that reference after CI passes.

The build action creates a local candidate with fresh base/OS layers. The caller
must test it before scanning and exporting it. The publish action loads exactly
that archive, requires the caller to scan it against the current vulnerability database, pushes
an immutable run tag and only then promotes latest on the default branch.
No PR event may publish. Application tests stay in each product repository.

`default.json` is the shared Renovate policy. Automated merge is gated by the
consumer's required CI checks. Major/prerelease updates remain manual.
The independent maintenance service is deployed separately on the operator's
server; credentials and private repository inventory do not belong here.
