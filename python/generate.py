"""Create a Unifically task, wait for it, print the output URL.

Usage:
  export UNIFICALLY_API_KEY=...
  python generate.py video            # google/veo-3.1-fast
  python generate.py image            # openai/gpt-image-2
  python generate.py music            # suno-ai/music
  python generate.py speech           # elevenlabs/text-to-speech
  python generate.py video --dry-run  # price check only, nothing is charged

Model pages (parameters and a browser playground):
  https://unifically.com/models/veo-3.1
  https://unifically.com/models/gpt-image-2
  https://unifically.com/models/suno
  https://unifically.com/models/elevenlabs
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("UNIFICALLY_API_BASE_URL", "https://api.unifically.com").rstrip("/")
KEY = os.environ.get("UNIFICALLY_API_KEY")

EXAMPLES = {
    "video": ("google/veo-3.1-fast", {"prompt": "A golden retriever running along a beach at sunset, slow motion, cinematic lighting", "duration": 8}),
    "image": ("openai/gpt-image-2", {"prompt": "A cozy wooden cabin in a snowy forest at dusk, warm light in the windows, photorealistic", "resolution": "1K"}),
    "music": ("suno-ai/music", {"mv": "chirp-hawk", "custom": False, "gpt_description_prompt": "An upbeat indie pop song about a summer road trip, bright guitars, catchy chorus"}),
    "speech": ("elevenlabs/text-to-speech", {"text": "Welcome to Unifically. This voice was generated with a single API call."}),
}


def call(method, path, body=None):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            # Cloudflare rejects urllib's default user agent with a 403 (error 1010).
            "User-Agent": "unifically-examples/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as err:
        sys.exit(f"HTTP {err.code}: {err.read().decode(errors='replace')[:500]}")


def main():
    if not KEY:
        sys.exit("Set UNIFICALLY_API_KEY first. Keys are at https://unifically.com/api-keys")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kind = args[0] if args else "image"
    if kind not in EXAMPLES:
        sys.exit(f"Pick one of: {', '.join(EXAMPLES)}")
    model, payload = EXAMPLES[kind]

    if "--dry-run" in sys.argv:
        # Validates the request and returns the price. No task is created.
        # The Suno routes do not support dry_run yet.
        res = call("POST", "/v1/tasks", {"model": model, "input": payload, "dry_run": True})
        print(f"{model} would cost ${res['data']['cost']}")
        return

    task = call("POST", "/v1/tasks", {"model": model, "input": payload})["data"]
    print(f"task {task['task_id']} created, status {task['status']}")

    while True:
        time.sleep(5)
        data = call("GET", f"/v1/tasks/{task['task_id']}")["data"]
        if data["status"] == "completed":
            print(json.dumps(data["output"], indent=2))
            return
        if data["status"] == "failed":
            sys.exit(f"task failed: {data.get('error_message')}")
        print("  still", data["status"])


if __name__ == "__main__":
    main()
