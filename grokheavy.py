"""GrokHeavy — interactive CLI for xAI's multi-agent Grok research workflow.

Runs Grok's multi-agent ("Heavy") mode with optional server-side tools
(web search, X search, code execution, collections search), streams the
answer with a Rich UI, and saves each turn to a local session folder.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search, code_execution, collections_search
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt

console = Console()

# Current multi-agent ("Grok Heavy") model. xAI retired the dated beta id
# (grok-4.20-multi-agent-beta-0309); the stable alias is below.
MODEL = "grok-4.20-multi-agent"

CONFIG_FILE = Path(os.environ.get("GROKHEAVY_CONFIG", "grokheavy_config.json"))
LOG_DIR = Path(os.environ.get("GROKHEAVY_SESSIONS", "grokheavy_sessions"))


def load_api_key():
    """Return an xAI API key from the environment, a saved config, or a prompt."""
    env_key = os.environ.get("XAI_API_KEY")
    if env_key:
        console.print("[green]Loaded API key from XAI_API_KEY[/green]")
        return env_key.strip()

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            api_key = json.load(f).get("api_key")
        if api_key:
            console.print(f"[green]Loaded API key from {CONFIG_FILE}[/green]")
            return api_key

    api_key = Prompt.ask("Enter your xAI API key", password=True).strip()
    if Prompt.ask("Save API key for future runs? (y/n)", default="y").lower() == "y":
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": api_key}, f)
        console.print(f"[green]API key saved to {CONFIG_FILE}[/green]")
    return api_key


def select_tools():
    """Prompt for which server-side tools to enable and return the list."""
    console.print("\n[bold]Enable tools[/bold]")
    tools = []
    if Prompt.ask("Web Search?", default="y").lower() == "y":
        tools.append(web_search())
    if Prompt.ask("X (Twitter) Search?", default="y").lower() == "y":
        tools.append(x_search())
    if Prompt.ask("Code Execution?", default="y").lower() == "y":
        tools.append(code_execution())

    collection_ids = Prompt.ask(
        "Collections to search? (comma-separated IDs, blank to skip)", default=""
    ).strip()
    if collection_ids:
        ids = [c.strip() for c in collection_ids.split(",") if c.strip()][:10]
        tools.append(collections_search(collection_ids=ids))
        console.print(f"[green]Collections search enabled for {len(ids)} collection(s)[/green]")

    return tools


def read_prompt():
    """Read a multi-line prompt, sent on two consecutive blank lines."""
    console.print("\n[bold]You[/bold] (paste then press Enter twice to send, or type /help):")
    lines = []
    blanks = 0
    while True:
        line = input()
        lines.append(line)
        if not line.strip():
            blanks += 1
            if blanks >= 2:
                break
        else:
            blanks = 0
    return "\n".join(lines).strip()


def export_markdown(session_name, conv_id, question, response):
    LOG_DIR.mkdir(exist_ok=True)
    md_file = LOG_DIR / f"{session_name}_{conv_id}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# GrokHeavy — {session_name}\n\n**Question:** {question}\n\n{response}")
    console.print(f"[green]Exported to {md_file}[/green]")


def stream_answer(chat):
    """Stream one response, showing reasoning progress, and return the text."""
    console.print("\n[bold magenta]GrokHeavy swarm thinking...[/bold magenta]")
    full_response = ""
    with Live(Spinner("dots", text="Agents collaborating + tools active"),
              console=console, refresh_per_second=4) as live:
        is_thinking = True
        for response, chunk in chat.stream():
            reasoning = getattr(getattr(response, "usage", None), "reasoning_tokens", 0)
            if reasoning and is_thinking:
                live.update(Spinner("dots", text=f"Reasoning tokens: {reasoning}"))
            if chunk.content:
                if is_thinking:
                    live.stop()
                    console.print("\n[bold green]Final answer[/bold green]\n")
                    is_thinking = False
                console.print(chunk.content, end="", style="white")
                full_response += chunk.content
    console.print("\n")
    return full_response


def main():
    console.print("[bold green]GrokHeavy[/bold green] — multi-agent Grok research CLI")
    console.print("[dim]Streaming output • server-side tools • local session exports[/dim]\n")

    client = Client(api_key=load_api_key())
    tools = select_tools()
    agent_count = 16 if Prompt.ask("Use 16 agents (deep research)?", default="y").lower() == "y" else 4

    def new_chat():
        return client.chat.create(
            model=MODEL, agent_count=agent_count, tools=tools, include=["verbose_streaming"]
        )

    chat = new_chat()
    conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_name = "Untitled"
    last_question = last_response = None

    console.print(f"\n[bold cyan]Session started:[/bold cyan] {session_name} ({agent_count} agents)")

    while True:
        question = read_prompt()
        if not question:
            continue

        if question.startswith("/"):
            parts = question.split(maxsplit=1)
            cmd = parts[0].lower()
            if cmd == "/help":
                console.print("[yellow]Commands: /new, /export, /attach <file>, /tools, /quit[/yellow]")
                continue
            if cmd == "/new":
                chat = new_chat()
                conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                session_name = Prompt.ask("New session name", default="Untitled")
                last_question = last_response = None
                console.print("[green]New session started[/green]")
                continue
            if cmd == "/tools":
                console.print(f"[yellow]Enabled: {', '.join(t.__class__.__name__ for t in tools) or 'none'}[/yellow]")
                continue
            if cmd == "/export":
                if last_response:
                    export_markdown(session_name, conv_id, last_question, last_response)
                else:
                    console.print("[red]Nothing to export yet[/red]")
                continue
            if cmd == "/quit":
                break
            if cmd == "/attach":
                if len(parts) < 2:
                    console.print("[red]Usage: /attach <file>[/red]")
                    continue
                try:
                    with open(parts[1].strip(), "r", encoding="utf-8") as f:
                        attached = f.read()
                except OSError:
                    console.print("[red]File not found[/red]")
                    continue
                console.print(f"[green]Attached {parts[1].strip()}. Now type your prompt.[/green]")
                follow_up = read_prompt()
                if not follow_up:
                    continue
                question = f"{attached}\n\n{follow_up}"
            else:
                console.print(f"[red]Unknown command: {cmd}[/red]")
                continue

        chat.append(user(question))
        response = stream_answer(chat)

        last_question, last_response = question, response
        LOG_DIR.mkdir(exist_ok=True)
        log_entry = {
            "session": session_name,
            "timestamp": datetime.now().isoformat(),
            "agents": agent_count,
            "question": question,
            "response": response,
            "tools_used": [t.__class__.__name__ for t in tools],
        }
        filename = LOG_DIR / f"{session_name}_{conv_id}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2)
        export_markdown(session_name, conv_id, question, response)
        console.print(f"[dim]Saved to {filename}[/dim]")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Bye.[/dim]")
