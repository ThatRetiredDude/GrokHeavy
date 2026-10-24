<div align="center">

# 🧠 GrokHeavy

**Point it at a question, pick your tools, hit Enter twice — a swarm of Grok agents researches it for you.**

A small terminal app that drives xAI's multi-agent ("Grok Heavy") mode: 4 or 16 agents reasoning in parallel, with web search, 𝕏 search, code execution and collections search, streamed live to your terminal and saved to disk.

[![PyPI](https://img.shields.io/pypi/v/grokheavy?style=for-the-badge&logo=pypi&logoColor=white&color=3775A9)](https://pypi.org/project/grokheavy/)
[![License: MIT](https://img.shields.io/github/license/ThatRetiredDude/GrokHeavy?style=for-the-badge&color=yellow)](LICENSE)
[![Stars](https://img.shields.io/github/stars/ThatRetiredDude/GrokHeavy?style=for-the-badge&logo=github&color=gold)](https://github.com/ThatRetiredDude/GrokHeavy/stargazers)

![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![xAI SDK](https://img.shields.io/badge/xai--sdk-grok--4.20--multi--agent-000000?style=flat-square)
![Grok Heavy](https://img.shields.io/badge/mode-multi--agent-1DA1F2?style=flat-square)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

</div>

---

## ⚠️ Cost warning

**A single run can be expensive.** 16-agent runs with tools enabled burn a lot of tokens and billed tool usage. The most expensive single request in testing was about **$5**; your costs vary with prompt size, agent count and tools. Watch your [xAI console](https://console.x.ai/) usage and limits before long research sessions. Start with 4 agents when you're just trying it out.

## ✨ What it does

- 🐝 **4 or 16 agents.** Pick quick-and-focused or deep-research at startup.
- 🔧 **Server-side tools, toggled per session.** Web search, 𝕏 search, code execution, and collections search over your own document collections.
- 📡 **Live streaming output** with a reasoning-token spinner while the swarm thinks.
- 💾 **Every turn saved** as JSON and Markdown under `grokheavy_sessions/`.
- ⌨️ **Slash commands** for new sessions, file attach, export and tool status.
- 🔑 **Key from env, config or prompt** — keep it out of the repo.

## 🚀 Setup

### 1. Install

<details open>
<summary><b>With pipx (recommended — isolated, gives you a <code>grokheavy</code> command)</b></summary>

```bash
pipx install grokheavy
grokheavy
```
</details>

<details>
<summary><b>With pip</b></summary>

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install grokheavy
grokheavy
```
</details>

<details>
<summary><b>From source</b></summary>

```bash
git clone https://github.com/ThatRetiredDude/GrokHeavy.git
cd GrokHeavy
python -m venv .venv
source .venv/bin/activate
pip install -e .
grokheavy          # or: python grokheavy.py
```
</details>

### 2. Give it an xAI API key

Get a key with multi-agent access from the [xAI console](https://console.x.ai/). GrokHeavy looks for it in this order:

1. The `XAI_API_KEY` environment variable (nothing is written to disk).
2. A saved `grokheavy_config.json` in the working directory.
3. A password prompt on first run, which can optionally save to `grokheavy_config.json`.

> `grokheavy_config.json` and `grokheavy_sessions/` are git-ignored. Don't commit your key.

### 3. Ask something

Paste your prompt, then press **Enter on two blank lines** to send. Answers stream in and are saved automatically.

## 🔧 Tools

At startup you choose which server-side tools the agents may use:

| Tool | What it does |
|---|---|
| 🌐 **Web Search** | Live web results. |
| 𝕏 **X Search** | Posts and threads on 𝕏. |
| 💻 **Code Execution** | Runs code in a sandbox to compute or verify answers. |
| 📚 **Collections Search** | Searches your own xAI document collections. Enter up to 10 collection IDs (comma-separated) when prompted; leave blank to skip. |

## ⌨️ Slash commands

| Command | What it does |
|---|---|
| `/help` | List commands. |
| `/new` | Start a fresh session (clears context, asks for a name). |
| `/attach <file>` | Read a text file, then prompt you for a question to send with it. |
| `/export` | Write the last answer to `grokheavy_sessions/<name>_<id>.md`. |
| `/tools` | Show which tools are enabled. |
| `/quit` | Exit. |

## ⚙️ Configuration

| Variable | Default | What it does |
|---|---|---|
| `XAI_API_KEY` | — | API key; takes priority over the saved config. |
| `GROKHEAVY_CONFIG` | `grokheavy_config.json` | Path to the saved-key file. |
| `GROKHEAVY_SESSIONS` | `grokheavy_sessions` | Where JSON/Markdown transcripts are written. |

The model is **`grok-4.20-multi-agent`**, set as `MODEL` in `grokheavy.py`. xAI may rename or retire beta models; update that constant if your account uses a different id.

## 🩺 Troubleshooting

<details>
<summary><b>404 / model not found</b></summary>

Your account may not have multi-agent access, or the model id changed. Confirm access in the [xAI console](https://console.x.ai/) and update `MODEL` in `grokheavy.py` if needed.
</details>

<details>
<summary><b>It just sits on "Agents collaborating…"</b></summary>

16-agent runs with tools take a while before the first token. Give it time; the spinner shows reasoning-token progress once the swarm starts thinking.
</details>

<details>
<summary><b>Collections search errors</b></summary>

Collection IDs must be real collections on your xAI account, and you can pass at most 10. Leave the prompt blank to disable the tool.
</details>

<details>
<summary><b>My prompt won't send</b></summary>

Send is triggered by **two** consecutive blank lines, so press Enter twice after your text.
</details>

## 🧑‍💻 Development

```bash
pip install -e . build twine
python -m build          # builds the wheel + sdist into dist/
python -m twine check dist/*
```

## 📜 License

MIT — see [LICENSE](LICENSE).
