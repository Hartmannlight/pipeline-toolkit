#!/usr/bin/env bash
set -euo pipefail

# Retrying the same immutable tag is safe: the candidate never changes here.
retry() {
  local attempt
  for attempt in 1 2 3; do
    if "$@"; then return 0; fi
    if [[ "$attempt" == 3 ]]; then return 1; fi
    echo "Registry operation failed; retrying attempt $((attempt + 1))/3" >&2
    sleep "$((attempt * 5))"
  done
}

immutable="$IMAGE:sha-$GITHUB_SHA-r$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT"
docker tag "$CANDIDATE" "$immutable"
retry docker push "$immutable"
digest=$(retry docker buildx imagetools inspect "$immutable" --format '{{json .Manifest.Digest}}' | tr -d '"')
[[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]]
echo "digest=$digest" >> "$GITHUB_OUTPUT"
echo "Published $immutable@$digest" >> "$GITHUB_STEP_SUMMARY"
