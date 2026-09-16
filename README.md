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

Python application dependencies managed through PEP 621/uv use exact requirements.
This keeps uv lock resolution aligned with Renovate's minimum release age instead
of allowing an open lower bound to select a newer, unapproved release. Python
interpreter compatibility ranges and Poetry library requirements are unchanged.

Renovate preserves `project.requires-python` compatibility minimums. Raising that
minimum is a deliberate compatibility change, not a runtime security update.
Docker Python images, interpreter pins, dependencies and lockfiles remain updated.

Go module directives and `golang` compiler images are updated together as the
`Go toolchain` group, so readonly builds do not require a newer compiler than
the pinned builder provides.

For Poetry, the isolated `poetry-core` build-system requirement is updated without
trying to install it as a project dependency through `poetry.lock`. This exception
is limited to that backend declaration; application dependency artifacts remain
mandatory.
