# Reviewed inline producer tail. Embed in the adopter workflow AFTER its lane
# cage has signed the original commit. Do not execute a checkout program with
# the producer's token. Required caller data: DEFAULT_BRANCH, OBSERVATION_CLOCK,
# GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT, GITHUB_REPOSITORY, GH_TOKEN and RUNNER_TEMP.
set -euo pipefail
case "${OBSERVATION_CLOCK}" in drift-sample|twin-sweep) ;; *) echo '::error::unknown observation clock'; exit 1 ;; esac
[[ "${GITHUB_RUN_ID}" =~ ^[1-9][0-9]*$ && "${GITHUB_RUN_ATTEMPT}" =~ ^[1-9][0-9]*$ ]] || { echo '::error::invalid observation run or attempt'; exit 1; }
head="$(git rev-parse --abbrev-ref HEAD)"
if [ "${GITHUB_REF_NAME}" != "${DEFAULT_BRANCH}" ] || [ "${head}" != "${DEFAULT_BRANCH}" ]; then
  echo '::error::observation delivery requires the checked-out default branch'
  exit 1
fi
DELIVERY_BRANCH="observations/${OBSERVATION_CLOCK}/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
ORIGINAL_OBSERVATION="$(git rev-parse HEAD)"
# Refuse an existing branch even when Git would call the identical SHA up to
# date. The lease below independently closes the race after this read.
if git ls-remote --exit-code --heads origin "refs/heads/${DELIVERY_BRANCH}" >/dev/null 2>&1; then
  echo "::error::observation ref already exists; refusing to update ${DELIVERY_BRANCH}"
  exit 1
fi
# Atomic absence CAS: an explicitly EMPTY expected old object prevents updating
# any existing ref, including an ancestor ref created during advertisement.
# Publish the original object before any integration; never replay or move it.
git push --force-with-lease="refs/heads/${DELIVERY_BRANCH}:" origin HEAD:"${DELIVERY_BRANCH}"
body="${RUNNER_TEMP}/observation-delivery-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}.md"
printf '%s\n' \
  "Original signed ${OBSERVATION_CLOCK} observation from run ${GITHUB_RUN_ID}, attempt ${GITHUB_RUN_ATTEMPT}." \
  '' \
  "Pending original commit: ${ORIGINAL_OBSERVATION}." \
  '' \
  'PENDING: the signed observation is durable on its unique ref and is not recorded on the default branch yet.' \
  'A separate trusted reviewer validates exact run, certificate claims and append-only bytes before ordinary protected-branch review and a merge preserving the original object.' \
  > "${body}"
gh pr create --repo "${GITHUB_REPOSITORY}" --base "${DEFAULT_BRANCH}" --head "${DELIVERY_BRANCH}" \
  --title "${OBSERVATION_CLOCK}: deliver run ${GITHUB_RUN_ID} attempt ${GITHUB_RUN_ATTEMPT}" --body-file "${body}"
echo "PENDING: original observation ${ORIGINAL_OBSERVATION} published to ${DELIVERY_BRANCH}; not recorded on ${DEFAULT_BRANCH} until reviewed delivery."
