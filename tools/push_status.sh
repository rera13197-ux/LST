#!/usr/bin/env bash
# Second publishing phase: record the content-commit hashes in the status
# documents and push ONE small fast-forward commit per branch (no force).
#
#   tools/push_lst.sh main . "..."      # phase 1: content commits
#   tools/push_lst.sh <branch> ...      # phase 1: one per exercise
#   tools/push_status.sh                # phase 2: this file
#
# A commit cannot contain its own hash.  Phase 1 therefore pushes the content
# with placeholder hashes; this script reads those hashes from the remote,
# regenerates the status docs with them, and adds a child commit whose tree
# differs only in PROJECT_PROGRESS.md, EXERCISE_BRANCH_INDEX.md and
# output/push_hashes.json.  Every branch tip stays a fast-forward of its
# content commit.
set -euo pipefail

REMOTE="${LST_REMOTE:-https://github.com/rera13197-ux/LST.git}"
GITROOT="$(git rev-parse --show-toplevel)"
REPO="${GITROOT}/lst"
cd "$GITROOT"

python3 "${REPO}/tools/record_hashes.py"
python3 "${REPO}/tools/update_docs.py" >/dev/null
echo "status documents regenerated with the content hashes"

status_commit() {
  BR="$1"
  EXISTING="$(git ls-remote --heads "$REMOTE" "refs/heads/${BR}" | head -n1 | cut -f1 || true)"
  if [ -z "$EXISTING" ]; then
    echo "branch ${BR} does not exist on ${REMOTE}; run push_lst.sh first" >&2
    return 1
  fi
  git fetch -q "$REMOTE" "refs/heads/${BR}"

  IDX="$(mktemp -u /tmp/lst-status.XXXXXX)"
  export GIT_INDEX_FILE="${IDX}"
  git read-tree FETCH_HEAD
  for p in PROJECT_PROGRESS.md EXERCISE_BRANCH_INDEX.md output/push_hashes.json; do
    [ -e "${REPO}/${p}" ] || continue
    BLOB="$(git hash-object -w "${REPO}/${p}")"
    git update-index --add --cacheinfo "100644,${BLOB},${p}"
  done
  ENTRIES="$(git ls-files | wc -l | tr -d ' ')"
  if [ "$ENTRIES" -lt 3 ]; then
    echo "refusing to push ${BR}: only ${ENTRIES} staged paths" >&2
    unset GIT_INDEX_FILE
    rm -f "${IDX}"
    return 1
  fi
  TREE="$(git write-tree)"
  unset GIT_INDEX_FILE
  rm -f "${IDX}"

  COMMIT="$(git commit-tree "${TREE}" -p "${EXISTING}" \
              -m "LST: record published branch hashes")"
  LOCAL_REF="refs/heads/push-status-${BR}"
  git update-ref "${LOCAL_REF}" "${COMMIT}"
  git push "$REMOTE" "${LOCAL_REF}:refs/heads/${BR}"
  git update-ref -d "${LOCAL_REF}"
  echo "status ${BR} -> ${COMMIT:0:8} (${ENTRIES} paths)"
}

for b in main \
  Exercise-1-LST-Introduction \
  Exercise-2-LST-EDF-RM-Comparison \
  Exercise-3-LST-Manual-Scheduling \
  Exercise-4-LST-Optimality-And-Overload \
  Exercise-5-LST-Presentation \
  Exercise-6-LST-Paper-And-Seminar \
  Exercise-7-LST-Tie-Breaking-And-Thrashing; do
  status_commit "$b"
done
