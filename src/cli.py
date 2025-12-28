"""
Claude Code Helper - Interactive CLI
A tool to help generate effective prompts for Claude Code based on repository analysis.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.syntax import Syntax
from rich import box

from .analyzer import RepoAnalyzer
from .generator import CoreGenerator, PromptGenerator


console = Console()


def print_header():
    """Print the application header."""
    console.print(Panel.fit(
        "[bold blue]Claude Code Helper[/bold blue]\n"
        "[dim]Repository Prompt Generator[/dim]",
        border_style="blue"
    ))
    console.print()


def print_analysis_summary(analysis):
    """Print a summary of the repository analysis."""
    table = Table(title="Repository Analyse", box=box.ROUNDED)
    table.add_column("Eigenschap", style="cyan")
    table.add_column("Waarde", style="green")

    table.add_row("Naam", analysis.name)
    table.add_row("Totaal bestanden", str(analysis.total_files))
    table.add_row("Regels code", f"{analysis.total_lines:,}")

    if analysis.languages:
        langs = ", ".join([f"{k} ({v})" for k, v in list(analysis.languages.items())[:3]])
        table.add_row("Talen", langs)

    if analysis.frameworks:
        table.add_row("Frameworks", ", ".join(analysis.frameworks))

    if analysis.technologies:
        table.add_row("Technologieen", ", ".join(analysis.technologies[:5]))

    console.print(table)
    console.print()


def ask_clarification_questions(questions, prompt_gen):
    """Ask clarification questions and collect answers."""
    if not questions:
        return {}

    console.print("\n[bold yellow]Verduidelijkingsvragen[/bold yellow]")
    console.print("[dim]Beantwoord de volgende vragen voor een betere prompt:[/dim]\n")

    answers = {}
    for i, q in enumerate(questions[:5], 1):  # Max 5 questions
        importance_color = {
            "high": "red",
            "medium": "yellow",
            "low": "dim"
        }.get(q.importance, "white")

        console.print(f"[{importance_color}]({q.importance})[/{importance_color}] {q.question}")

        if q.context:
            console.print(f"  [dim italic]{q.context}[/dim italic]")

        if q.options:
            console.print(f"  [dim]Opties: {', '.join(q.options)}[/dim]")

        answer = Prompt.ask("  Antwoord", default="[overslaan]")

        if answer != "[overslaan]":
            answers[q.question] = answer

        console.print()

    return answers


def display_generated_prompt(result):
    """Display the generated prompt and recommendations."""
    # Show task type
    console.print(Panel(
        f"[bold]Gedetecteerd taaktype:[/bold] {result.task_type.value.replace('_', ' ').title()}",
        border_style="blue"
    ))

    # Show approach
    console.print("\n[bold green]Aanbevolen Aanpak[/bold green]")
    console.print(Markdown(result.approach))

    # Show the generated prompt
    console.print("\n[bold cyan]Gegenereerde Prompt[/bold cyan]")
    console.print(Panel(
        result.prompt,
        title="Kopieer deze prompt naar Claude Code",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Show tips
    if result.tips:
        console.print("\n[bold yellow]Tips voor Effectief Gebruik[/bold yellow]")
        for tip in result.tips:
            console.print(f"  • {tip}")

    # Show warnings
    if result.warnings:
        console.print("\n[bold red]Aandachtspunten[/bold red]")
        for warning in result.warnings:
            console.print(f"  ⚠ {warning}")

    # Show follow-up prompts
    if result.follow_up_prompts:
        console.print("\n[bold magenta]Vervolgprompts[/bold magenta]")
        console.print("[dim]Na voltooiing kun je deze prompts gebruiken:[/dim]")
        for i, follow_up in enumerate(result.follow_up_prompts, 1):
            console.print(f"  {i}. {follow_up}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Claude Code Helper - Generate effective prompts for Claude Code."""
    pass


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', type=click.Path(), help='Output path for core file')
def analyze(repo_path, output):
    """Analyze a repository and generate a core context file."""
    print_header()

    console.print(f"[bold]Analyseren van repository:[/bold] {repo_path}\n")

    with console.status("[bold green]Repository analyseren..."):
        analyzer = RepoAnalyzer(repo_path)
        analysis = analyzer.analyze()

    print_analysis_summary(analysis)

    # Generate core file
    core_gen = CoreGenerator(analysis)

    if output:
        content = core_gen.generate(output)
        console.print(f"[green]✓[/green] Kernbestand gegenereerd: {output}")
    else:
        content = core_gen.generate()
        output_path = Path(repo_path) / ".claude-context.md"
        console.print(f"[green]✓[/green] Kernbestand gegenereerd: {output_path}")

    console.print("\n[dim]Dit bestand geeft Claude context over je repository.[/dim]")


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True), default='.')
@click.option('--goal', '-g', type=str, help='Your goal or task description')
@click.option('--quick', '-q', is_flag=True, help='Generate a quick prompt without questions')
def prompt(repo_path, goal, quick):
    """Generate an optimized prompt for Claude Code."""
    print_header()

    console.print(f"[bold]Repository:[/bold] {repo_path}\n")

    # Analyze repository
    with console.status("[bold green]Repository analyseren..."):
        analyzer = RepoAnalyzer(repo_path)
        analysis = analyzer.analyze()

    print_analysis_summary(analysis)

    # Initialize generators
    core_gen = CoreGenerator(analysis)
    prompt_gen = PromptGenerator(analysis, core_gen)

    # Get goal if not provided
    if not goal:
        console.print("[bold]Wat wil je bereiken?[/bold]")
        console.print("[dim]Beschrijf je doel zo specifiek mogelijk.[/dim]")
        goal = Prompt.ask("\nDoel")

    if not goal:
        console.print("[red]Geen doel opgegeven. Gestopt.[/red]")
        return

    console.print()

    if quick:
        # Quick mode - generate prompt directly
        quick_prompt = prompt_gen.get_quick_prompt(goal)
        console.print("[bold cyan]Snelle Prompt[/bold cyan]")
        console.print(Panel(quick_prompt, border_style="cyan"))
    else:
        # Full mode - ask clarification questions
        task_type = prompt_gen.classify_task(goal)
        questions = prompt_gen.get_clarification_questions(goal, task_type)

        console.print(f"[dim]Gedetecteerd taaktype: {task_type.value}[/dim]")

        if questions:
            answers = ask_clarification_questions(questions, prompt_gen)
        else:
            answers = {}

        # Generate prompt
        result = prompt_gen.generate_prompt(goal, answers, task_type)

        display_generated_prompt(result)

    # Offer to save
    console.print()
    if Confirm.ask("Kernbestand opslaan in repository?", default=True):
        core_gen.generate()
        console.print("[green]✓[/green] Kernbestand opgeslagen als .claude-context.md")


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True), default='.')
def interactive(repo_path):
    """Start an interactive session for generating prompts."""
    print_header()

    console.print(f"[bold]Repository:[/bold] {repo_path}\n")

    # Analyze repository
    with console.status("[bold green]Repository analyseren..."):
        analyzer = RepoAnalyzer(repo_path)
        analysis = analyzer.analyze()

    print_analysis_summary(analysis)

    # Initialize generators
    core_gen = CoreGenerator(analysis)
    prompt_gen = PromptGenerator(analysis, core_gen)

    # Save core file
    core_gen.generate()
    console.print("[green]✓[/green] Kernbestand gegenereerd: .claude-context.md\n")

    console.print("[bold]Interactieve modus[/bold]")
    console.print("[dim]Typ 'exit' of 'quit' om te stoppen.[/dim]")
    console.print("[dim]Typ 'help' voor tips.[/dim]\n")

    while True:
        try:
            goal = Prompt.ask("\n[bold cyan]Wat wil je bereiken?[/bold cyan]")

            if goal.lower() in ['exit', 'quit', 'q']:
                console.print("[dim]Tot ziens![/dim]")
                break

            if goal.lower() == 'help':
                show_help()
                continue

            if goal.lower() == 'analyze':
                print_analysis_summary(analysis)
                continue

            if not goal.strip():
                continue

            # Classify and get questions
            task_type = prompt_gen.classify_task(goal)
            console.print(f"\n[dim]Taaktype: {task_type.value}[/dim]")

            # Ask if user wants clarification questions
            if Confirm.ask("Wil je verduidelijkingsvragen beantwoorden voor een betere prompt?", default=True):
                questions = prompt_gen.get_clarification_questions(goal, task_type)
                answers = ask_clarification_questions(questions, prompt_gen)
            else:
                answers = {}

            # Generate and display prompt
            result = prompt_gen.generate_prompt(goal, answers, task_type)
            display_generated_prompt(result)

        except KeyboardInterrupt:
            console.print("\n[dim]Tot ziens![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Fout: {e}[/red]")


def show_help():
    """Show help information."""
    help_text = """
## Beschikbare Commando's

- **analyze** - Toon repository analyse opnieuw
- **exit/quit** - Stop de interactieve modus
- **help** - Toon deze hulp

## Tips voor Effectieve Prompts

1. **Wees specifiek** - Noem exacte bestanden of functies
2. **Geef context** - Beschrijf waarom je iets wilt
3. **Splits complexe taken** - Vraag om één ding per keer
4. **Beschrijf gewenst resultaat** - Wat moet het eindresultaat zijn?

## Voorbeelden van Goede Doelen

- "Fix de bug in src/api/auth.py waar login faalt bij speciale tekens"
- "Voeg een dark mode toggle toe aan de settings pagina"
- "Refactor de UserService class voor betere testbaarheid"
- "Optimaliseer de database queries in het rapport module"
"""
    console.print(Markdown(help_text))


@cli.command()
def tips():
    """Show best practices for using Claude Code."""
    print_header()

    tips_text = """
# Best Practices voor Claude Code Prompts

## 1. Wees Specifiek en Expliciet
❌ "Fix de bugs"
✓ "Fix de bug in src/auth.py:45 waar de login functie crasht bij lege passwords"

## 2. Geef Context
❌ "Voeg caching toe"
✓ "Voeg Redis caching toe aan de getUser functie in UserService om database load te verminderen"

## 3. Splits Complexe Taken
❌ "Bouw een complete authentication system"
✓ "Stap 1: Analyseer de huidige auth structuur en geef een plan"
✓ "Stap 2: Implementeer de login endpoint"
✓ "Stap 3: Voeg session management toe"

## 4. Vraag om Lezing Eerst
✓ "Lees eerst src/services/user.py en leg uit hoe de auth flow werkt"
✓ "Analyseer de bestaande test structuur voordat je nieuwe tests schrijft"

## 5. Specificeer Output Format
✓ "Geef een plan met genummerde stappen voordat je code schrijft"
✓ "Leg na elke wijziging uit wat je hebt veranderd en waarom"

## 6. Set Constraints
✓ "Behoud backwards compatibility met de v1 API"
✓ "Gebruik geen externe dependencies"
✓ "Volg de bestaande code stijl"

## 7. Itereer
- Begin met een plan/analyse
- Review het plan
- Implementeer stap voor stap
- Valideer elke stap
"""
    console.print(Markdown(tips_text))


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
