---
name: unifically
description: Generate video, images, music, speech and text through the UnificAlly API (one key for Veo, Kling, Seedance, Sora, FLUX, Nano Banana, Suno, ElevenLabs, Claude, GPT, Gemini and 150+ other models) using the `uai` CLI or plain HTTP. Use when the user asks to generate or edit a video, image, song, voiceover or sound effect, transcribe audio, call an LLM through UnificAlly, check what a generation will cost, or wire UnificAlly into code.
---

# UnificAlly

[UnificAlly](https://unifically.com) is one API key for 150+ generative models: video, image, audio and LLMs. Media jobs are async tasks. LLMs use the OpenAI or Anthropic request format.

- Docs (every model id and its inputs): [docs.unifically.com](https://docs.unifically.com)
- Full docs as one file for agents: [llms-full.txt](https://docs.unifically.com/llms-full.txt)
- CLI: [unifically.com/cli](https://unifically.com/cli) · MCP server: [unifically.com/mcp](https://unifically.com/mcp)
- Code examples (Python, Node, curl, Postman, n8n): [unifically-examples](https://github.com/unifically-dev/unifically-examples)

## Setup

```bash
npm install -g @unifically/cli
uai auth login            # or: export UNIFICALLY_API_KEY=sk-...
uai auth status
```

Keys come from [unifically.com/api-keys](https://unifically.com/api-keys). Never print the key or commit it.

## Rules

1. **Never guess a model id or a parameter.** Models are added and changed often. Find the id with `uai models --search <name> --type video|image|audio|llm`, then read that model's page on [docs.unifically.com](https://docs.unifically.com) (or `uai models <provider/model>`) before the first run.
2. **Check the cost before anything expensive** (video, long audio, 4K, batches): `uai cost <model> key=value ...`. Tell the user the price and wait for an OK. Tasks bill when they run and cannot be cancelled once submitted.
3. **Inputs are URLs.** In the CLI pass local files with `key=@file` (`image_url=@photo.png`) or `--image photo.png`, and they are uploaded for you. From code, upload first with `uai upload ./photo.png` (prints a `file_url`) and pass that URL. Third-party URLs often fail upstream; use the uploaded URL.
4. **Failed tasks are not charged.** If a task fails, read `error_message`, fix the input and retry once. Do not loop.
5. Save outputs into the user's project with `-o <path>`, not a temp folder they will never find.

## Common jobs

```bash
# Video (Veo 3.1, sound included). Read the model page for allowed duration/aspect_ratio/resolution.
uai cost google/veo-3.1-fast prompt="a fox walking through snow, slow dolly in" duration=8
uai run google/veo-3.1-fast prompt="a fox walking through snow, slow dolly in" duration=8 --sync -o fox.mp4

# Image
uai run black-forest-labs/flux.2-pro prompt="product shot of a matte black mug on oak" aspect_ratio=1:1 --sync -o mug.png

# Image-to-video from a local file (uploaded automatically; check the model page for the frame field name)
uai run google/veo-3.1-fast prompt="slow orbit around the mug" --first-image mug.png duration=8 --sync -o mug.mp4

# Speech
uai resources elevenlabs voices --search sarah
uai run elevenlabs/text-to-speech text="Welcome back." voice="Sarah" --sync -o welcome.mp3

# Music (Suno returns two songs per task)
uai run suno-ai/music mv=chirp-hawk custom=false gpt_description_prompt="upbeat lo-fi intro for a tech podcast" --sync -o intro.mp3

# LLM
uai run anthropic/claude-sonnet-5-5 "summarize this file" < notes.md
```

Long jobs: run with `--async`, keep the task id, then `uai wait <task_id> -o out.mp4` or `uai status <task_id>`. Add `--json` to any command for machine-readable output; `uai exec <command>` streams JSONL events for scripts.

## Calling the API from code

Media models:

```bash
curl -X POST https://api.unifically.com/v1/tasks \
  -H "Authorization: Bearer $UNIFICALLY_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "google/veo-3.1-fast", "input": {"prompt": "a fox in snow", "duration": 8}}'
# -> {"data": {"task_id": "...", "status": "processing"}}

curl https://api.unifically.com/v1/tasks/TASK_ID -H "Authorization: Bearer $UNIFICALLY_API_KEY"
# poll every 5-15 s until data.status is "completed" (result in data.output) or "failed" (data.error_message)
```

- Add `"dry_run": true` to the create body to get the price without running the job.
- Pass `"callback_url"` instead of polling when the code has a public endpoint ([webhooks](https://docs.unifically.com/api-reference/callbacks)).

LLMs: point any OpenAI SDK at `https://api.unifically.com/v1` (`/chat/completions`, `/responses`) or any Anthropic SDK at `https://api.unifically.com` (`/v1/messages`), with the UnificAlly key and a `provider/model` id such as `openai/gpt-5.5` or `anthropic/claude-sonnet-5-5`.

## MCP instead of the CLI

If the agent supports MCP and no terminal is available:

```bash
claude mcp add --transport http unifically https://mcp.unifically.com/mcp --header "Authorization: Bearer $UNIFICALLY_API_KEY"
```

The same rules apply: read the model page first, `dry_run_cost` before expensive jobs.
