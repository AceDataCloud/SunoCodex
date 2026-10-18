---
name: suno
description: Use Suno through Ace Data Cloud for music generation, custom lyrics, song extension and covers, or retrieve an existing Suno task. This is an independent service plugin, not a general chat model provider.
---

# Suno by Ace Data Cloud

Use the plugin's `suno` MCP tools. Do not fall back to another provider/model or silently submit a second request.

## First use

1. Read [the setup guide](../../README.md) and check that the service key is available to the Codex process through `ACEDATACLOUD_API_TOKEN`. Never ask the user to paste it into chat or echo it.
2. Inspect the current tool input schema. Use `suno_list_models` for a no-generation connectivity check.
3. Explain that generation/editing can incur charges. Use only the model, action, inputs and spending scope approved by the user. Do not infer permission to spend from installing the plugin.
4. For an authorized media request, submit once. Preserve the task ID and use `suno_get_task` until terminal success or failure. Pending is not completed output; never regenerate to poll. Show returned media only after a successful terminal result.
5. Keep task/trace ID for support, never the key. Report 401/403 as auth/access failures, 429 as rate limit, and server errors without relabeling them as success. Stop repeated failures instead of retrying paid submissions.

## Available tool scope

| Tool | Boundary |
| --- | --- |
| `suno_list_models` | Read model/operation guidance; does not submit media. |
| `suno_list_actions` | See connected tool schema and current pricing before use. |
| `suno_generate_music` | See connected tool schema and current pricing before use. |
| `suno_generate_custom_music` | See connected tool schema and current pricing before use. |
| `suno_extend_music` | See connected tool schema and current pricing before use. |
| `suno_cover_music` | See connected tool schema and current pricing before use. |
| `suno_get_task` | Query existing task; keep the same task ID. |
| `suno_get_tasks_batch` | Query existing task; keep the same task ID. |

This is a client package over the existing hosted MCP; it does not implement or change service pricing, defaults or routing.
