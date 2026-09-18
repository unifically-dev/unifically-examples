# n8n workflows

Import a `.json` file in n8n (Workflows, Import from file). No community node needed, only the built-in HTTP Request node, so they run on n8n Cloud too.

| File | Model |
|---|---|
| `veo-3.1-text-to-video.json` | `google/veo-3.1-fast` |
| `gemini-omni-flash-text-to-video.json` | `google/gemini-omni-flash-1.1-video` |

## Setup

1. Get an API key at https://unifically.com/api-keys
2. In n8n create a **Header Auth** credential. Name: `Authorization`. Value: `Bearer YOUR_KEY`
3. Select it in the two HTTP Request nodes (`Create task`, `Get task`)
4. Activate the workflow, open the form URL from the `Prompt form` node, submit a prompt

## Swap the model

Open the **Settings** node. `model` is the model id and `input` is the request body for that model. Nothing else depends on the model. Model ids and inputs are in https://docs.unifically.com

Failed tasks are not charged. The `Generation failed` node shows the API's error message.

## Add a workflow

Add an entry to `WORKFLOWS` in `build.py`, then run `python build.py`.
