"""
AI Personal Gym Coach — CLI Entrypoint
=======================================
Run with:
    python main.py

Or for a single command:
    python main.py --message "I ate 4 roti and 1 bowl dal"

Or to run the demo walkthrough:
    python main.py --demo
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

# Make sure project root is on the path regardless of working directory
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel   import Panel
from rich.prompt  import Prompt
from rich         import box

from graphs import gym_coach_graph

console = Console()

BANNER = """
[bold cyan]
  ╔══════════════════════════════════════════╗
  ║   🏋️   AI PERSONAL GYM COACH  🏋️        ║
  ║        Powered by LangGraph              ║
  ╚══════════════════════════════════════════╝
[/bold cyan]
[dim]Type [bold]help[/bold] to see all commands.  Type [bold]quit[/bold] to exit.[/dim]
"""

HELP_TEXT = """
[bold yellow]What can I do?[/bold yellow]

  [cyan]Profile & Targets[/cyan]
    "Set up my profile: I'm 22, male, 82kg, 175cm, fat loss goal, moderate activity,
     vegetarian, budget ₹4000"
    "Calculate my macros"

  [cyan]Diet[/cyan]
    "Generate my weekly diet plan"
    "I ate 4 roti, 1 bowl dal, 200g paneer for lunch"
    "Show my grocery list"

  [cyan]Workouts[/cyan]
    "Create my workout plan"
    "Log workout: Bench Press 60kg 10 10 8 7, Shoulder Press 40kg 12 12 10"

  [cyan]Tracking[/cyan]
    "Weight today: 81.5 kg"
    "Weekly check-in: weight 81.5, energy high, hunger medium, sleep 7 hours"

  [cyan]Meta[/cyan]
    help    → show this menu
    quit    → exit
"""


def run_graph(user_input: str) -> str:
    """Invoke the gym coach graph with a single user message."""
    result = gym_coach_graph.invoke({"user_input": user_input})
    return result.get("agent_response", "⚠️  No response generated.")


def interactive_loop() -> None:
    """REPL loop for interactive use."""
    console.print(BANNER)
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! Keep pushing 💪[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye! Keep pushing 💪[/dim]")
            break

        if user_input.lower() in ("help", "h", "?"):
            console.print(HELP_TEXT)
            continue

        console.print()
        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            response = run_graph(user_input)

        console.print(
            Panel(
                response,
                title="[bold cyan]🤖  Coach[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )


# ── Demo walkthrough ──────────────────────────────────────────────────────────
DEMO_MESSAGES = [
    (
        "Profile Setup",
        "My name is Arjun. I'm 22 years old, male, 82kg, 175cm tall. "
        "My goal is fat loss. Activity level is moderate. I'm vegetarian. "
        "Monthly budget ₹4000. Gym experience: beginner. Target weight 75kg. Sleep 7 hours.",
    ),
    (
        "Macro Calculation",
        "Calculate my daily calorie and macro targets",
    ),
    (
        "Diet Plan",
        "Generate my weekly vegetarian diet plan",
    ),
    (
        "Food Log",
        "For lunch I ate 4 roti, 1 bowl dal, and 200g paneer",
    ),
    (
        "Workout Plan",
        "Create a beginner gym workout plan for fat loss",
    ),
    (
        "Workout Log",
        "Logged today's workout: Bench Press 50kg sets 10 10 8, "
        "Shoulder Press 30kg sets 12 12 10, Tricep Pushdown 25kg sets 15 15 12",
    ),
    (
        "Weight Tracking",
        "Weight today: 81.8 kg",
    ),
    (
        "Grocery List",
        "Show me my weekly grocery shopping list",
    ),
    (
        "Weekly Check-In",
        "Weekly check-in: weight 81.5 kg, energy level medium, hunger low, slept 7 hours. "
        "Feeling good but a bit tired mid-week.",
    ),
]


def run_demo() -> None:
    """Run a guided demo walkthrough hitting every feature."""
    console.print(BANNER)
    console.print(
        Panel(
            "[bold yellow]🎬  DEMO MODE[/bold yellow] — Running all 9 features in sequence.\n"
            "This will make real LLM calls. Make sure OPENAI_API_KEY is set.",
            border_style="yellow",
        )
    )

    for i, (title, message) in enumerate(DEMO_MESSAGES, 1):
        console.print(f"\n[bold magenta]── Step {i}: {title} ──────────────────────────[/bold magenta]")
        console.print(f"[green]You:[/green] {message}\n")

        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            response = run_graph(message)

        console.print(
            Panel(
                response,
                title=f"[bold cyan]🤖  Coach — {title}[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )
        console.input("\n[dim]Press Enter for next step...[/dim]")

    console.print("\n[bold green]✅  Demo complete! All features demonstrated.[/bold green]")


# ── Argparse entry ─────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Personal Gym Coach powered by LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --demo
  python main.py --message "Calculate my macros"
        """,
    )
    parser.add_argument(
        "--message", "-m",
        type=str,
        default=None,
        help="Send a single message and print the response (non-interactive)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the guided feature demo walkthrough",
    )
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.message:
        response = run_graph(args.message)
        console.print(
            Panel(
                response,
                title="[bold cyan]🤖  Coach[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )
    else:
        interactive_loop()


if __name__ == "__main__":
    main()
