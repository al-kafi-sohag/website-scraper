import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from main import process_websites
from process_address import process_data
from add_google_map_link import main as add_google_maps
from retry_errors import main_retry, get_latest_error_file

console = Console()

def display_banner():
    banner = """
    🏢 Web Scraping Pipeline Manager 🔄
    ================================
    """
    console.print(Panel(banner, style="bold blue"))

def run_with_spinner(message, func, *args):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(description=f"[cyan]{message}...", total=None)
        result = func(*args)
        progress.update(task, completed=True)
    return result

def main_pipeline():
    display_banner()
    
    # Gather all user choices and inputs upfront
    choices = {
        "scrape": Confirm.ask("Do you want to start the main scraping process?"),
        "process_addresses": Confirm.ask("Do you want to process addresses?"),
        "add_maps": Confirm.ask("Do you want to add Google Maps links?"),
        "retry_errors": Confirm.ask("Do you want to retry failed operations?")
    }
    
    # Gather additional inputs if needed
    max_rows = 500
    
    if choices["process_addresses"]:
        max_rows_input = console.input("[cyan]Enter maximum number of addresses to process (default: 500): [/cyan]")
        max_rows = int(max_rows_input) if max_rows_input.isdigit() else 100
    
    if choices["retry_errors"]:
        error_csv_input = console.input(f"[cyan]Enter error CSV path (default: last error file): [/cyan]")
        error_csv = error_csv_input if error_csv_input else None
    
    # Execute based on user choices
    if choices["scrape"]:
        console.print("\n[yellow]Step 1: Website Scraping[/yellow]")
        csv_path = 'data/websites.csv'
        run_with_spinner("Running main scraping process", process_websites, csv_path)
        console.print("[green]✓[/green] Main scraping completed\n")
    
    if choices["process_addresses"]:
        console.print("\n[yellow]Step 2: Address Processing[/yellow]")
        run_with_spinner(
            "Processing addresses",
            process_data,
            "results/results.csv",
            max_rows
        )
        console.print("[green]✓[/green] Address processing completed\n")
    
    if choices["add_maps"]:
        console.print("\n[yellow]Step 3: Google Maps Links[/yellow]")
        run_with_spinner(
            "Adding Google Maps links",
            add_google_maps,
            "results/results.csv"
        )
        console.print("[green]✓[/green] Google Maps links added\n")
    
    if choices["retry_errors"]:
        console.print("\n[yellow]Step 4: Error Retry[/yellow]")
        run_with_spinner(
            "Retrying failed operations",
            main_retry,
            error_csv if error_csv is not None else get_latest_error_file()
        )
        console.print("[green]✓[/green] Error retry process completed\n")
    
    console.print("\n[green]Scraping execution completed![/green]")

if __name__ == "__main__":
    try:
        main_pipeline()
    except KeyboardInterrupt:
        console.print("\n[red]Process interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {str(e)}[/red]")