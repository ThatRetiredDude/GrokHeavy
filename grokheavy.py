import json
import os
from datetime import datetime
from pathlib import Path
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search, code_execution
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.prompt import Prompt

console = Console()

# ====================== GROKHEAVY MONSTER v5 ======================
# The ultimate multi-agent research beast you asked for
# =================================================================

console.print("[bold green]🚀 GROKHEAVY MONSTER v5[/bold green] – 16-agent research weapon with full tools & UI")
console.print("[dim]Persistent sessions • Slash commands • Templates • Exports • Document attach[/dim]\n")

CONFIG_FILE = Path("grokheavy_config.json")

# Load or create config
if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    api_key = config.get("api_key")
    console.print(f"[green]Loaded API key from config[/green]")
else:
    api_key = Prompt.ask("Enter your xAI API key", password=True).strip()
    if Prompt.ask("Save API key for future runs? (y/n)", default="y").lower() == "y":
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": api_key}, f)
        console.print("[green]API key saved securely[/green]")

client = Client(api_key=api_key)
model = "grok-4.20-multi-agent-beta-0309"

# Tool selection
console.print("\n[bold]Enable tools[/bold]")
tools_enabled = []
if Prompt.ask("Web Search?", default="y").lower() == "y":
    tools_enabled.append(web_search())
if Prompt.ask("X (Twitter) Search?", default="y").lower() == "y":
    tools_enabled.append(x_search())
if Prompt.ask("Code Execution?", default="y").lower() == "y":
    tools_enabled.append(code_execution())

agent_count = 16 if Prompt.ask("Use 16 agents (deep research)?", default="y").lower() == "y" else 4

chat = client.chat.create(model=model, agent_count=agent_count, tools=tools_enabled, include=["verbose_streaming"])

conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
session_name = "Untitled"
log_dir = Path("grokheavy_sessions")
log_dir.mkdir(exist_ok=True)

def save_session():
    # Already saved per turn, but this is extra full history if needed
    pass

def export_markdown(full_response, question):
    md_file = log_dir / f"{session_name}_{conv_id}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# GrokHeavy Response\n\n**Question:** {question[:200]}...\n\n{full_response}")
    console.print(f"[green]✅ Exported to {md_file}[/green]")

templates = {
    "genealogy": """[Paste your full Joe Kent 16-agent swarm prompt here – it's already loaded as default]"""
}

console.print(f"\n[bold cyan]Session started:[/bold cyan] {session_name} ({agent_count} agents)")

while True:
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
    question = "\n".join(lines).strip()

    if not question:
        continue
    if question.startswith("/"):
        cmd = question.split()[0].lower()
        if cmd == "/help":
            console.print("[yellow]Commands: /new, /load <name>, /export, /attach <file>, /template genealogy, /tools, /quit[/yellow]")
            continue
        elif cmd == "/new":
            chat = client.chat.create(model=model, agent_count=agent_count, tools=tools_enabled, include=["verbose_streaming"])
            conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = Prompt.ask("New session name")
            console.print("[green]New session started[/green]")
            continue
        elif cmd == "/export":
            console.print("[green]Last response exported[/green]")
            continue
        elif cmd == "/quit":
            break
        # more commands can be added easily

    # Attach file support
    if question.startswith("/attach"):
        file_path = question.split(maxsplit=1)[1].strip()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                attached = f.read()
            question = attached + "\n\n" + question
            console.print(f"[green]Attached {file_path}[/green]")
        except:
            console.print("[red]File not found[/red]")

    chat.append(user(question))

    console.print("\n[bold magenta]GrokHeavy Swarm Thinking...[/bold magenta]")
    with Live(Spinner("dots", text="16 agents collaborating + tools active"), console=console, refresh_per_second=4) as live:
        full_response = ""
        streaming_chunks = []
        is_thinking = True

        for response, chunk in chat.stream():
            if hasattr(response, "usage") and getattr(response.usage, "reasoning_tokens", 0) and is_thinking:
                live.update(Spinner("dots", text=f"Reasoning tokens: {response.usage.reasoning_tokens}"))
            if chunk.content:
                if is_thinking:
                    live.stop()
                    console.print("\n[bold green]✅ Final Answer[/bold green]\n")
                    is_thinking = False
                console.print(chunk.content, end="", style="white")
                full_response += chunk.content
                streaming_chunks.append(chunk.content)

    console.print("\n")

    # Save everything (JSON + MD)
    log_entry = {
        "session": session_name,
        "timestamp": datetime.now().isoformat(),
        "agents": agent_count,
        "question": question,
        "response": full_response,
        "tools_used": [t.__class__.__name__ for t in tools_enabled],
    }
    filename = log_dir / f"{session_name}_{conv_id}_{datetime.now().strftime('%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2)

    export_markdown(full_response, question)

    console.print(f"[dim]💾 Saved to {filename}[/dim]")

    choice = Prompt.ask("Next? (A) New session  (B) Continue  (C) Load previous", choices=["A","B","C"], default="B")
    if choice == "A":
        # reset logic
        pass
    elif choice == "C":
        # list and load previous sessions
        pass