# GrokHeavy

Interactive CLI for xAI’s **multi-agent Grok** research workflow: optional web search, X search, and code execution, with Rich-based streaming output and local session exports.

## Cost warning

**A single request can be expensive.** Multi-agent runs with tools enabled use a lot of tokens and billed tool usage. The most expensive single request in testing so far was about **$5**—your costs will vary with prompt size, agent count, and tools. Watch your [xAI console](https://console.x.ai/) usage and limits before large prompts or long research sessions.

## Requirements

- Python 3.10+ (3.12+ recommended)
- An [xAI API key](https://console.x.ai/) with access to the multi-agent model used in the script

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

On first run, the tool can prompt for your API key and optionally save it to `grokheavy_config.json` in the project directory.

- **Do not commit** `grokheavy_config.json`; it is listed in `.gitignore`.
- Session transcripts and exports go under `grokheavy_sessions/` (also ignored by default).

## Run

```bash
python grokheavy.py
```

You will be asked which tools to enable (web search, X search, code execution) and whether to use 16 agents or 4.

### Input

- Paste your prompt, then press **Enter twice** (two blank lines) to send.
- Slash commands (see in-app `/help`): e.g. `/help`, `/new`, `/quit`. Some commands are stubs in the current script.

### Outputs

- Per-turn **JSON** logs and **Markdown** exports under `grokheavy_sessions/`.

## Model

The script targets the model id configured in `grokheavy.py` (`grok-4.20-multi-agent-beta-0309` at time of writing). xAI may rename or retire beta models; update the `model` variable if your account uses a different id.

## License

MIT — see [LICENSE](LICENSE).
