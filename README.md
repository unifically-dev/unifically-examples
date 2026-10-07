# Unifically API examples

Working examples for the [Unifically API](https://docs.unifically.com): Python, Node, curl and a Postman collection. Video, image, music and speech generation all go through one endpoint, `POST /v1/tasks`.

Every request body here is the one the Unifically model pages generate, and each was run against the live API before it was committed.

## Before you start

1. Make an account at [unifically.com](https://unifically.com). New accounts get a $0.50 balance to test with.
2. Create a key at [unifically.com/api-keys](https://unifically.com/api-keys).
3. Put it in your environment:

```bash
export UNIFICALLY_API_KEY=your_key
```

## Check a price without paying

Add `"dry_run": true` to any task request. The API validates the body and returns the cost. No task is created and nothing is charged.

```bash
python python/generate.py video --dry-run
node node/generate.mjs image --dry-run
bash curl/quickstart.sh
```

Prices change, so nothing in this repo hardcodes one. The dry run is the source of truth, and the full list is at [unifically.com/pricing](https://unifically.com/pricing). The Suno routes do not support `dry_run` yet.

## Generate something

These calls are charged to your balance.

```bash
python python/generate.py image     # openai/gpt-image-2
python python/generate.py video     # google/veo-3.1-fast
python python/generate.py music     # suno-ai/music
python python/generate.py speech    # elevenlabs/text-to-speech
```

`node node/generate.mjs <kind>` does the same with Node 18 or newer. Neither script has dependencies.

The models these examples call, with a playground and the full parameter list on each page:

- [Veo 3.1 API](https://unifically.com/models/veo-3.1) (`google/veo-3.1-fast`)
- [GPT Image 2 API](https://unifically.com/models/gpt-image-2) (`openai/gpt-image-2`)
- [Suno API](https://unifically.com/models/suno) (`suno-ai/music`)
- [ElevenLabs text-to-speech API](https://unifically.com/models/elevenlabs) (`elevenlabs/text-to-speech`)
- [Seedance 2.0 API](https://unifically.com/models/seedance-2.0) and [Kling 3.0 API](https://unifically.com/models/kling-3.0) (Postman price checks)
- [Gemini Omni Flash 1.1 API](https://unifically.com/models/gemini-omni-flash-1.1) (n8n workflow)

Each script creates the task, polls `GET /v1/tasks/{task_id}` every five seconds, and prints `data.output` when the status is `completed`. The output holds `video_url`, `image_url` or `audio_url` depending on the model.

## The request shape

```json
{
  "model": "google/veo-3.1-fast",
  "input": { "prompt": "A cat walking on the beach at sunset", "duration": 8 },
  "callback_url": "https://your-server.com/webhook"
}
```

`model` is `provider/model-name`. `input` holds the parameters for that model, which differ between models; each model page at [unifically.com/models](https://unifically.com/models) lists them. `callback_url` is optional and sits at the top level, next to `model`.

Text models use the OpenAI and Anthropic compatible endpoints (`/v1/chat/completions`, `/v1/responses`, `/v1/messages`) instead of `/v1/tasks`. They are not covered here.

## Webhooks

Send `callback_url` and the API will POST to it when the task completes or fails, so you can skip polling. `python/webhook_flask.py` and `node/webhook_express.mjs` receive the callback and verify its signature.

Signing is off by default. Turn it on in the dashboard under Settings and you get a 64 character hex secret. Each delivery then carries `x-webhook-timestamp` and `x-webhook-signature`, where the signature is the hex HMAC-SHA256 of `timestamp + "." + raw_body`. Verify against the raw bytes, because re-serialized JSON will not match.

## Postman

Import `postman/unifically.postman_collection.json` and set the `api_key` collection variable. The collection has three folders:

- Price check: five dry run requests across video, image and speech models. Free to run.
- Create: charged requests. Each one saves its `task_id` to the collection.
- Tasks: get status and list tasks. Get status reads the saved `task_id`.

## One thing that will trip you up

The API sits behind Cloudflare, which rejects Python's default `urllib` user agent with `403` and `error code: 1010`. Send any `User-Agent` header and it goes through. `python/generate.py` already does.

## Agents and the terminal

There is also an [MCP server](https://github.com/unifically-dev/unifically-mcp) for Claude, Cursor and other agents, and a CLI described at [unifically.com/cli](https://unifically.com/cli).

## License

MIT
