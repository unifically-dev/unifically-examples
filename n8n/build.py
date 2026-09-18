"""Builds the n8n workflow JSON files in this folder.

Every workflow is the same eight nodes. Only the form fields and the two
values in the "Settings" node (model, input) differ, so a new model is one
entry in WORKFLOWS below, or one edit to the Settings node inside n8n.

    python build.py
"""
import json
import pathlib
import uuid

HERE = pathlib.Path(__file__).parent
NS = uuid.UUID("6f1d8a52-3b7e-4c0a-9d51-0e6b7a4c2f10")


def nid(workflow, node):
    return str(uuid.uuid5(NS, f"{workflow}:{node}"))


def dropdown(label, values, required=True):
    return {
        "fieldLabel": label,
        "fieldType": "dropdown",
        "fieldOptions": {"values": [{"option": v} for v in values]},
        "requiredField": required,
    }


WORKFLOWS = [
    {
        "file": "veo-3.1-text-to-video.json",
        "name": "Generate a video with Google Veo 3.1 (Unifically API)",
        "form_title": "Veo 3.1 video generator",
        "form_description": "Type a prompt, get a Veo 3.1 video with sound.",
        "fields": [
            {"fieldLabel": "Prompt", "fieldType": "textarea", "requiredField": True,
             "placeholder": "A golden retriever running along a beach at sunset, slow motion"},
            dropdown("Aspect ratio", ["16:9", "9:16"]),
            dropdown("Duration", ["4", "6", "8"]),
        ],
        "model": "google/veo-3.1-fast",
        "model_note": "Other Veo 3.1 tiers: google/veo-3.1-lite, google/veo-3.1-quality, google/veo-3.1-lite-relaxed",
        "input": "={{ { prompt: $json.Prompt, aspect_ratio: $json['Aspect ratio'], duration: Number($json.Duration), resolution: '720p' } }}",
    },
    {
        "file": "gemini-omni-flash-text-to-video.json",
        "name": "Generate a video with Gemini Omni Flash 1.1 (Unifically API)",
        "form_title": "Gemini Omni Flash video generator",
        "form_description": "Type a prompt, get a Gemini Omni Flash 1.1 video with sound. Up to 10 seconds.",
        "fields": [
            {"fieldLabel": "Prompt", "fieldType": "textarea", "requiredField": True,
             "placeholder": "A street musician plays violin in the rain, handheld camera"},
            dropdown("Aspect ratio", ["16:9", "9:16"]),
            dropdown("Duration", ["4", "6", "8", "10"]),
        ],
        "model": "google/gemini-omni-flash-1.1-video",
        "model_note": "To edit an existing video instead, use google/gemini-omni-flash-1.1-video-edit and add reference_video_urls to the input",
        "input": "={{ { prompt: $json.Prompt, aspect_ratio: $json['Aspect ratio'], duration: Number($json.Duration), resolution: '720p' } }}",
    },
]

AUTH = {
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
}
CRED = {"httpHeaderAuth": {"id": "REPLACE_ME", "name": "Unifically API key"}}


def build(w):
    key = w["file"]
    sticky = (
        f"## {w['name']}\n\n"
        "**Setup (2 minutes)**\n"
        "1. Get an API key at https://unifically.com/api-keys\n"
        "2. In n8n create a **Header Auth** credential. Name: `Authorization`. Value: `Bearer YOUR_KEY`\n"
        "3. Select that credential in both HTTP Request nodes\n"
        "4. Open the form URL from the first node and submit a prompt\n\n"
        "**Swap the model**\n"
        "Open the **Settings** node. `model` is the model id, `input` is the request body for that model. "
        "Nothing else in the workflow depends on the model.\n\n"
        f"{w['model_note']}.\n\n"
        "All model ids and their inputs: https://docs.unifically.com"
    )
    nodes = [
        {
            "id": nid(key, "note"), "name": "Read me", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
            "position": [-560, -420], "parameters": {"content": sticky, "height": 420, "width": 520},
        },
        {
            "id": nid(key, "form"), "name": "Prompt form", "type": "n8n-nodes-base.formTrigger", "typeVersion": 2.2,
            "position": [-520, 80], "webhookId": nid(key, "webhook"),
            "parameters": {
                "formTitle": w["form_title"],
                "formDescription": w["form_description"],
                "formFields": {"values": w["fields"]},
                "responseMode": "lastNode",
                "options": {},
            },
        },
        {
            "id": nid(key, "settings"), "name": "Settings", "type": "n8n-nodes-base.set", "typeVersion": 3.4,
            "position": [-300, 80],
            "parameters": {
                "assignments": {"assignments": [
                    {"id": nid(key, "a1"), "name": "api_base", "type": "string", "value": "https://api.unifically.com"},
                    {"id": nid(key, "a2"), "name": "model", "type": "string", "value": w["model"]},
                    {"id": nid(key, "a3"), "name": "input", "type": "object", "value": w["input"]},
                    {"id": nid(key, "a4"), "name": "poll_seconds", "type": "number", "value": 10},
                ]},
                "options": {},
            },
        },
        {
            "id": nid(key, "create"), "name": "Create task", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [-80, 80], "credentials": CRED,
            "parameters": {
                "method": "POST",
                "url": "={{ $json.api_base }}/v1/tasks",
                **AUTH,
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ model: $json.model, input: $json.input }) }}",
                "options": {},
            },
        },
        {
            "id": nid(key, "wait"), "name": "Wait", "type": "n8n-nodes-base.wait", "typeVersion": 1.1,
            "position": [140, 80], "webhookId": nid(key, "waithook"),
            "parameters": {"amount": "={{ $('Settings').first().json.poll_seconds }}", "unit": "seconds"},
        },
        {
            "id": nid(key, "get"), "name": "Get task", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [360, 80], "credentials": CRED,
            "parameters": {
                "url": "={{ $('Settings').first().json.api_base }}/v1/tasks/{{ $('Create task').first().json.data.task_id }}",
                **AUTH,
                "options": {},
            },
        },
        {
            "id": nid(key, "switch"), "name": "Status?", "type": "n8n-nodes-base.switch", "typeVersion": 3.2,
            "position": [580, 80],
            "parameters": {
                "rules": {"values": [
                    {"outputKey": "completed", "renameOutput": True, "conditions": {
                        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                        "combinator": "and",
                        "conditions": [{"id": nid(key, "c1"), "leftValue": "={{ $json.data.status }}", "rightValue": "completed",
                                        "operator": {"type": "string", "operation": "equals"}}]}},
                    {"outputKey": "failed", "renameOutput": True, "conditions": {
                        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                        "combinator": "and",
                        "conditions": [{"id": nid(key, "c2"), "leftValue": "={{ $json.data.status }}", "rightValue": "failed",
                                        "operator": {"type": "string", "operation": "equals"}}]}},
                ]},
                "options": {"fallbackOutput": "extra", "renameFallbackOutput": "still running"},
            },
        },
        {
            "id": nid(key, "result"), "name": "Result", "type": "n8n-nodes-base.set", "typeVersion": 3.4,
            "position": [820, -60],
            "parameters": {
                "assignments": {"assignments": [
                    {"id": nid(key, "r1"), "name": "video_url", "type": "string", "value": "={{ $json.data.output.video_url }}"},
                    {"id": nid(key, "r2"), "name": "model", "type": "string", "value": "={{ $('Settings').first().json.model }}"},
                    {"id": nid(key, "r4"), "name": "task_id", "type": "string", "value": "={{ $json.data.task_id }}"},
                ]},
                "options": {},
            },
        },
        {
            "id": nid(key, "show"), "name": "Show video", "type": "n8n-nodes-base.form", "typeVersion": 1,
            "position": [1040, -60], "webhookId": nid(key, "showhook"),
            "parameters": {
                "operation": "completion",
                "completionTitle": "Your video is ready",
                "completionMessage": "={{ $json.video_url }}",
                "options": {},
            },
        },
        {
            "id": nid(key, "fail"), "name": "Generation failed", "type": "n8n-nodes-base.stopAndError", "typeVersion": 1,
            "position": [820, 100],
            "parameters": {"errorMessage": "={{ $json.data.error_message || 'The task failed. Failed tasks are not charged.' }}"},
        },
    ]
    connections = {
        "Prompt form": {"main": [[{"node": "Settings", "type": "main", "index": 0}]]},
        "Settings": {"main": [[{"node": "Create task", "type": "main", "index": 0}]]},
        "Create task": {"main": [[{"node": "Wait", "type": "main", "index": 0}]]},
        "Wait": {"main": [[{"node": "Get task", "type": "main", "index": 0}]]},
        "Get task": {"main": [[{"node": "Status?", "type": "main", "index": 0}]]},
        "Result": {"main": [[{"node": "Show video", "type": "main", "index": 0}]]},
        "Status?": {"main": [
            [{"node": "Result", "type": "main", "index": 0}],
            [{"node": "Generation failed", "type": "main", "index": 0}],
            [{"node": "Wait", "type": "main", "index": 0}],
        ]},
    }
    return {"name": w["name"], "nodes": nodes, "connections": connections, "active": False,
            "settings": {"executionOrder": "v1"}, "pinData": {}}


if __name__ == "__main__":
    for w in WORKFLOWS:
        (HERE / w["file"]).write_text(json.dumps(build(w), indent=2) + "\n", encoding="utf-8", newline="\n")
        print("wrote", w["file"])
