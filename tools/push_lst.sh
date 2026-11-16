#!/usr/bin/env bash
# Publish one exercise folder of the LST project onto its own long-lived branch
# of the target repository, **flattened**: the contents of <folder>/ become the
# branch root, so that README.md, code/, docs/, diagrams/, output/ and tests/
# sit at the top level of the branch and GitHub renders the exercise README
# directly when the branch is opened.
#
# The branch is NOT checked out: a temporary index is built from the branch tip
# (or from nothing, when the branch does not exist yet) and the resulting
# commit is pushed.
#
# Usage:
#   tools/push_lst.sh <branch> <folder> "<commit message>"
#   tools/push_lst.sh main . "message"          # push the whole tree as-is
#
# The remote defaults to REMOTE below and can be overridden with $LST_REMOTE.
#
# Implementation note (fixed 2026-11-16): staging must happen from the *git
# root* with GIT_WORK_TREE pointing at the folder.  Running ``git add -A`` from
# inside the folder keeps a ``lst/exercise-N/`` prefix in git's pathspec
# handling, silently producing an EMPTY tree.  The guard below refuses to push
# such a tree.  Repo-level status files are added by blob hash, not by pathspec,
# for the same reason.
set -euo pipefail

BR="${1:?branch name required}"
DIR="${2:?folder required}"
MSG="${3:?commit message required}"
REMOTE="${LST_REMOTE:-https://github.com/rera13197-ux/LST.git}"

GITROOT="$(git rev-parse --show-toplevel)"
REPO="${GITROOT}/lst"
cd "$GITROOT"
[ -d "$REPO/$DIR" ] || { echo "folder $DIR does not exist" >&2; exit 1; }

# Does the branch already exist on the remote?
EXISTING="$(git ls-remote --heads "$REMOTE" "refs/heads/${BR}" | head -n1 | cut -f1 || true)"

TMP_INDEX="$(mktemp -u /tmp/lst-index.XXXXXX)"
export GIT_INDEX_FILE="${TMP_INDEX}"

if [ -n "$EXISTING" ]; then
  git fetch -q "$REMOTE" "refs/heads/${BR}"
  git read-tree FETCH_HEAD
else
  echo "branch ${BR} does not exist on ${REMOTE} -- creating it"
fi

# 1. stage the folder at the branch ROOT (or the whole tree when DIR is ".")
if [ "$DIR" = "." ]; then
  GIT_WORK_TREE="$REPO" git add -A -- .
else
  GIT_WORK_TREE="$REPO/$DIR" git add -A -- .
fi

# 2. keep the repo-level files that belong on every branch, by blob hash.
for p in PROJECT_PROGRESS.md EXERCISE_BRANCH_INDEX.md; do
  if [ -e "$REPO/$p" ]; then
    BLOB="$(git hash-object -w "$REPO/$p")"
    git update-index --add --cacheinfo "100644,${BLOB},${p}"
  fi
done

# 3. never publish an accidentally empty (or almost empty) tree
ENTRIES="$(git ls-files | wc -l | tr -d ' ')"
if [ "$ENTRIES" -lt 3 ]; then
  echo "refusing to push: only ${ENTRIES} staged paths" >&2
  unset GIT_INDEX_FILE
  rm -f "${TMP_INDEX}"
  exit 1
fi

SAMPLE="$(git ls-files | head -8 | tr '\n' ' ')"
NESTED="$(git ls-files | grep -c '^lst/' || true)"
TREE="$(git write-tree)"

if [ "${LST_DRY_RUN:-0}" = "1" ]; then
  unset GIT_INDEX_FILE
  rm -f "${TMP_INDEX}"
  echo "DRY RUN ${DIR} -> ${BR}: entries=${ENTRIES} nested_lst=${NESTED} tree=${TREE}"
  echo "sample: ${SAMPLE}"
  exit 0
fi

unset GIT_INDEX_FILE
rm -f "${TMP_INDEX}"

if [ -n "$EXISTING" ]; then
  COMMIT="$(git commit-tree "${TREE}" -p "${EXISTING}" -m "${MSG}")"
else
  COMMIT="$(git commit-tree "${TREE}" -m "${MSG}")"
fi

LOCAL_REF="refs/heads/push-lst-${BR}"
git update-ref "${LOCAL_REF}" "${COMMIT}"
git push "$REMOTE" "${LOCAL_REF}:refs/heads/${BR}"
git update-ref -d "${LOCAL_REF}"

echo "pushed ${DIR} -> ${BR} as ${COMMIT:0:8} (${ENTRIES} paths)"
