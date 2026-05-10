import enum
from operator import le
import requests
import argparse
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import box
import os
import ast

console = Console()
API_URL = "http://localhost"

YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def add_watch_args(parser):
    parser.add_argument(
        "-w",
        "--watch",
        dest="watch",
        type=float,
        nargs="?",
        const=1.0,
        help="Watch mode: refresh every N seconds (default: 1.0)",
    )


parser = argparse.ArgumentParser(description="Nerva Engine CLI tools")

subparsers = parser.add_subparsers(dest="command", help="Nerva API Command")

parser.add_argument("--url", help="Override the API URL")
parser.add_argument("--key", help="Override the API Key")
parser.add_argument("--json", help="Print the output in raw JSON")

# == History ==
history_parser = subparsers.add_parser(
    "history", help="Get the information of the last LIMIT number of tasks"
)

# == Status ==
status_parser = subparsers.add_parser("status", help="Get details for a specific task")

# == Trigger ==
trigger_parser = subparsers.add_parser("trigger", help="Manually trigger a task")

# == Purge ==
purge_parser = subparsers.add_parser(
    "purge", help="Delete all data from the PostgreSQL database"
)

# == Tasks ==
tasks_parser = subparsers.add_parser(
    "tasks", help="List all registered task definitions"
)

# == Register ==
register_parser = subparsers.add_parser(
    "register", help="Register a local python file as a task"
)


register_parser.add_argument("file_path", help="Path to the .py file")
register_parser.add_argument("-t", "--task", help="Specific function name to register")
register_parser.add_argument(
    "-a", "--all", action="store_true", help="Register all functions in the file"
)


add_watch_args(history_parser)
add_watch_args(status_parser)

history_parser.add_argument(
    "-l",
    "--limit",
    help="Number of latest tasks to show. Use -1 to show all.",
    type=int,
    default=10,
    metavar="N",
)
history_parser.add_argument(
    "-s",
    "--status",
    help="Filter the returned items by their status",
    type=str,
    choices=["PENDING", "WORKING", "COMPLETED", "FAILED"],
)
history_parser.add_argument(
    "-v", "--verbose", action="store_true", help="Show all columns from the tasks table"
)
history_parser.add_argument(
    "-a",
    "--after",
    type=str,
    help="Show tasks after this date/time",
    metavar='"YYYY-MM-DD HH:MM:SS"',
)
history_parser.add_argument(
    "-b",
    "--before",
    type=str,
    help="Show tasks before this date/time",
    metavar='"YYYY-MM-DD HH:MM:SS"',
)

# === Status command ===
status_parser.add_argument(
    "task_id", help="The numerical ID of the task", type=int, metavar="ID"
)

# === Trigger command ===
trigger_parser.add_argument(
    "task_name", help="Name of the task to trigger", type=str, metavar="TASK_NAME"
)
trigger_parser.add_argument(
    "-p",
    "--params",
    nargs="+",
    help="Parameters as key-value pairs (e.g., seconds=10 repeat=5)",
)

args = parser.parse_args()


def get_history(
    verbose: bool,
    limit: int,
    status: str | None = None,
    before: str | None = None,
    after: str | None = None,
):
    query_params = {"limit": limit, "status": status, "before": before, "after": after}

    try:
        response = requests.get(f"{API_URL}/history", params=query_params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not fetch history. {e}")
        return

    if not data:
        console.print("[yellow]No tasks found in history.[/yellow]")
        return

    table = Table(
        title="[bold magenta]Nerva Task History[/bold magenta]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )

    table.add_column("ID", justify="right", style="dim")

    if verbose:
        table.add_column("Task Type", style="blue")
        table.add_column("Created At", style="dim", no_wrap=True)

    table.add_column("Status", justify="left")
    table.add_column("Result")

    for task in data:
        status = task.get("status", "UNKNOWN")
        status_colors = {
            "COMPLETED": "green",
            "FAILED": "red",
            "WORKING": "yellow",
            "PENDING": "cyan",
        }
        color = status_colors.get(status, "white")  # type: ignore

        row = [str(task.get("id"))]

        if verbose:
            row.append(task.get("task_type", "N/A"))
            created = task.get("created_at", "N/A").replace("T", " ")[:19]
            row.append(created)

        row.append(f"[{color}]{status}[/]")

        result = task.get("result") or task.get("payload", "")
        row.append(str(result))

        table.add_row(*row)

    # console.print("\n", table, "\n")
    return table


def get_task_status(id: int):
    response = requests.get(f"{API_URL}/status/{id}")

    if response.status_code == 404:
        console.print(
            f"[bold red]Error:[/bold red] Task {id} does not exist in the database."
        )
        return

    if response.status_code != 200:
        console.print(f"[yellow]Unexpected error:[/yellow] {response.status_code}")
        return

    task = response.json()

    status_colors = {
        "COMPLETED": "green",
        "FAILED": "red",
        "WORKING": "yellow",
        "PENDING": "cyan",
    }
    color = status_colors.get(task["status"], "white")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Task ID:", str(task["id"]))
    table.add_row("Type:", task.get("task_type", "N/A"))
    table.add_row("Status:", f"[{color} bold]{task['status']}[/]")
    table.add_row("Created:", task.get("created_at", "").replace("T", " ")[:19])

    res = task.get("result") or "No output yet."
    table.add_row("Result:", f"[italic]{res}[/]")

    # console.print(Panel(table, title=f"[bold]Task {id}[/]", expand=False, style=color))
    return Panel(table, title=f"[bold]Task {id}[/]", expand=False, style=color)


def trigger_task(task_name, param_list):
    payload = {"task_name": task_name, "params": {}}

    # Validating parameters
    if param_list:
        for item in param_list:
            try:
                key, value = item.split("=", 1)

                if value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit() and "." in value:
                    value = float(value)

                payload["params"][key] = value
            except ValueError:
                print(
                    f"{YELLOW}Warning:{RESET} Skipping invalid parameter '{item}'. Use key=value format."
                )

    # Sending the POST request
    try:
        response = requests.post(f"{API_URL}/trigger", json=payload)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("id")

        time.sleep(0.1)

        status_response = requests.get(f"{API_URL}/status/{task_id}")
        status_data = status_response.json()

        if status_data["status"] == "FAILED":
            error_msg = status_data.get("result", {}).get("error", "Unknown error")
            print(f"{RED}Validation Error:{RESET} {error_msg}")
        else:
            print(f"{GREEN}Success!{RESET} Triggered {task_name}. Task ID: {task_id}")

    except Exception as e:
        print(f"{RED}Error:{RESET} {e}")


def get_registered_tasks():
    if args.command == "tasks":
        response = requests.get(f"{API_URL}/tasks/definitions")
        defs = response.json()

        table = Table(title="Registered Task Blueprints")
        table.add_column("Name", style="cyan")
        table.add_column("Entrypoint", style="magenta")
        table.add_column("Params", style="green")

        for d in defs:
            table.add_row(d["name"], d["entrypoint"], str(d["params_schema"]))

        return table


def register_tasks(file_path, task_name=None, register_all=False):
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File {file_path} not found.")
        return

    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, start=os.getcwd())
    docker_path = os.path.join("/app", rel_path)  # f"/app/{file_name}"

    abs_path = os.path.abspath(file_path)

    found_tasks = {}
    with open(abs_path, "r") as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                params = {}

                defaults = [ast.unparse(d) for d in node.args.defaults]
                args = node.args.args
                padding = len(args) - len(defaults)

                for i, arg in enumerate(args):
                    arg_name = arg.arg

                    arg_type = "any"
                    if arg.annotation:
                        arg_type = ast.unparse(arg.annotation)

                    default_val = None
                    if i >= padding:
                        default_val = defaults[i - padding]

                    if default_val:
                        params[arg_name] = f"{arg_type} (default: {default_val})"
                    else:
                        params[arg_name] = arg_type

                found_tasks[node.name] = params

    to_register = []

    if register_all:
        to_register = found_tasks
        if task_name:
            console.print(
                f"[yellow]Note:[/yellow] --all is set, ignoring specific task '{task_name}' and registering everything from {file_name}"
            )
    elif task_name:
        if task_name in found_tasks:
            to_register = [task_name]
        else:
            console.print(
                f"[red]Error:[/red] Task '{task_name}' not found in {file_path}"
            )
            console.print(f"Available tasks: {', '.join(found_tasks)}")
            return
    else:
        console.print("[red]Error:[/red] You must provide either --task or --all")
        return

    for name in to_register:
        data = {
            "name": name.upper(),  # type:ignore
            "entrypoint": f"{docker_path}:{name}",
            "params_schema": found_tasks[name],
        }
        resp = requests.post(f"{API_URL}/tasks/register", json=data)
        if resp.status_code == 200:
            console.print(f"[green]Regsitered:[/green] {name.upper()}")  # type:ignore


# Checking subparser commands
if args.command == "history":
    if args.watch:
        with Live(
            get_history(args.verbose, args.limit, args.status, args.before, args.after),
            console=console,
        ) as live:
            try:
                while True:
                    time.sleep(args.watch)
                    live.update(
                        get_history(  # type: ignore
                            args.verbose,
                            args.limit,
                            args.status,
                            args.before,
                            args.after,
                        )
                    )
            except KeyboardInterrupt:
                pass
    else:
        console.print(
            get_history(args.verbose, args.limit, args.status, args.before, args.after)
        )


if args.command == "status":
    if args.watch:
        with Live(
            get_task_status(args.task_id), console=console, refresh_per_second=4
        ) as live:
            try:
                while True:
                    time.sleep(args.watch)
                    live.update(get_task_status(args.task_id))  # type: ignore
            except KeyboardInterrupt:
                pass
    else:
        console.print(get_task_status(args.task_id))

if args.command == "trigger":
    trigger_task(args.task_name, args.params)

if args.command == "tasks":
    console.print(get_registered_tasks())

if args.command == "register":
    register_tasks(args.file_path, args.task, args.all)
