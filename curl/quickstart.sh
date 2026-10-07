#!/usr/bin/env bash
# The API in three calls. Needs curl and a key in UNIFICALLY_API_KEY.
# Nothing in this script is charged: step 2 is a dry run.
# Model used: openai/gpt-image-2, see https://unifically.com/models/gpt-image-2
set -euo pipefail
API="${UNIFICALLY_API_BASE_URL:-https://api.unifically.com}"
AUTH="Authorization: Bearer ${UNIFICALLY_API_KEY:?set UNIFICALLY_API_KEY}"
BODY='{"model":"openai/gpt-image-2","input":{"prompt":"A cozy wooden cabin in a snowy forest at dusk","resolution":"1K"}}'

echo "1. account and balance"
curl -s "$API/v1/account" -H "$AUTH"; echo

echo "2. price check (dry_run, nothing is charged)"
curl -s -X POST "$API/v1/tasks" -H "$AUTH" -H "Content-Type: application/json" \
  -d "${BODY%\}},\"dry_run\":true}"; echo

echo "3. to create the task for real, send the same body without dry_run:"
echo "   curl -s -X POST $API/v1/tasks -H \"\$AUTH\" -H 'Content-Type: application/json' -d '$BODY'"
echo "   then poll: curl -s $API/v1/tasks/TASK_ID -H \"\$AUTH\""
