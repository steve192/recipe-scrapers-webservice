#!/usr/bin/env bash
# Starts the image and checks that gunicorn serves the API. Catches dependency updates that
# pass the unit tests but break the server on startup, before they are released unseen.
# Usage: scripts/smoke-test-image.sh <image>
set -euo pipefail

image="${1:?usage: $0 <image>}"
container=""

cleanup() {
  if [ -n "$container" ]; then
    docker rm -f "$container" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

fail() {
  echo "FAIL $*" >&2
  if [ -n "$container" ]; then
    docker logs "$container" >&2 || true
  fi
  exit 1
}

container=$(docker run -d -p 127.0.0.1::9090 "$image")
port=$(docker port "$container" 9090/tcp | head -n 1 | sed 's/.*://')
base="http://127.0.0.1:$port"

for _ in $(seq 1 50); do
  if curl -s -o /dev/null "$base/"; then
    break
  fi
  sleep 0.2
done

hosts=$(curl -fsS "$base/api/v1/scrape-recipe/supported-hosts") \
  || fail "/api/v1/scrape-recipe/supported-hosts did not answer with 2xx"
count=$(python3 -c 'import json, sys; hosts = json.load(sys.stdin); assert isinstance(hosts, list); print(len(hosts))' <<<"$hosts") \
  || fail "/api/v1/scrape-recipe/supported-hosts did not return a JSON list"
[ "$count" -gt 0 ] || fail "/api/v1/scrape-recipe/supported-hosts returned no hosts"
echo "ok   /api/v1/scrape-recipe/supported-hosts -> $count hosts"

status=$(curl -s -o /dev/null -w '%{http_code}' "$base/api/v1/scrape-recipe")
[ "$status" = 400 ] || fail "/api/v1/scrape-recipe without url expected 400, got $status"
echo "ok   /api/v1/scrape-recipe without url -> 400"

# Scrapes the test recipe through gunicorn. The unit tests run in the build stage, while the
# image ships a separate pip install of the exported requirements, so this is what proves that
# the parsing libraries work in the image that is released. The page is served from inside
# the container, so no outside network is needed.
docker exec -d "$container" python3 -m http.server 8000 --bind 127.0.0.1 --directory /app/tests
recipe_url="$base/api/v1/scrape-recipe?url=http://127.0.0.1:8000/example_recipe.html"
recipe=""
for _ in $(seq 1 50); do
  if recipe=$(curl -fsS "$recipe_url" 2>/dev/null); then
    break
  fi
  sleep 0.2
done
[ -n "$recipe" ] || fail "scraping the test recipe did not answer with 2xx"
python3 -c '
import json, sys
recipe = json.loads(sys.stdin.buffer.read())
assert recipe["title"] == "Non-Alcoholic Piña Colada", recipe["title"]
assert isinstance(recipe["ingredients"], list) and recipe["ingredients"], recipe["ingredients"]
assert isinstance(recipe["nutrients"], dict), recipe["nutrients"]
' <<<"$recipe" || fail "scraping the test recipe returned an unexpected recipe: $recipe"
echo "ok   /api/v1/scrape-recipe of the test recipe -> title, ingredients, nutrients"

echo "all checks passed"
