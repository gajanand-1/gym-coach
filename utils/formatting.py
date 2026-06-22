"""
Rich-based pretty-print helpers used by the CLI.
"""

from __future__ import annotations
from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich         import box

console = Console()


def print_panel(title: str, content: str, style: str = "bold cyan") -> None:
    console.print(Panel(content, title=title, border_style=style))


def print_macro_table(macros: dict) -> None:
    t = Table(title="🎯 Your Daily Targets", box=box.ROUNDED)
    t.add_column("Metric",  style="bold yellow")
    t.add_column("Value",   style="green")
    t.add_row("TDEE",       f"{macros.get('tdee_kcal', 0):.0f} kcal")
    t.add_row("Target",     f"{macros.get('target_kcal', 0):.0f} kcal")
    t.add_row("Protein",    f"{macros.get('protein_g', 0):.0f} g")
    t.add_row("Carbs",      f"{macros.get('carbs_g', 0):.0f} g")
    t.add_row("Fat",        f"{macros.get('fat_g', 0):.0f} g")
    console.print(t)


def print_food_summary(summary: dict) -> None:
    t = Table(title="🍽️  Today's Food Summary", box=box.ROUNDED)
    t.add_column("Macro",     style="bold yellow")
    t.add_column("Consumed",  style="green")
    t.add_column("Remaining", style="red")
    t.add_row("Calories",
              f"{summary.get('total_kcal', 0):.0f} kcal",
              f"{summary.get('remaining_kcal', 0):.0f} kcal")
    t.add_row("Protein",
              f"{summary.get('total_protein_g', 0):.0f} g",
              f"{summary.get('remaining_protein', 0):.0f} g")
    console.print(t)


def print_weight_trend(entries: list[dict]) -> None:
    if not entries:
        console.print("[yellow]No weight entries yet.[/yellow]")
        return
    t = Table(title="⚖️  Weight Trend", box=box.SIMPLE)
    t.add_column("Date",      style="cyan")
    t.add_column("Weight",    style="green")
    for e in entries[-10:]:   # last 10
        t.add_row(e["date"], f"{e['weight_kg']} kg")
    console.print(t)


def print_grocery_list(items: list[dict]) -> None:
    t = Table(title="🛒 Grocery List", box=box.ROUNDED)
    t.add_column("Item",      style="bold")
    t.add_column("Quantity",  style="cyan")
    t.add_column("Cost (₹)",  style="green")
    total = 0.0
    for item in items:
        cost = item.get("estimated_cost", 0)
        total += cost
        t.add_row(item["item"], item["quantity"], f"₹{cost:.0f}")
    t.add_row("[bold]TOTAL[/bold]", "", f"[bold]₹{total:.0f}[/bold]")
    console.print(t)
