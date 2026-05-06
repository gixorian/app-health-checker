import requests
import argparse
import time


API_URL = "http://localhost"

YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

parser = argparse.ArgumentParser(description="Nerva Engine CLI tools")

subparsers = parser.add_subparsers(dest="command", help="Nerva API Command")

parser.add_argument("--url", help="Override the API URL")
parser.add_argument("--key", help="Override the API Key")
parser.add_argument("--json", help="Print the output in raw JSON")

# === History command ===
history_parser = subparsers.add_parser(
    "history", help="Get the information of the last LIMIT number of tasks"
)
status_parser = subparsers.add_parser("status", help="Get details for a specific task")
trigger_parser = subparsers.add_parser("trigger", help="Manually trigger a task")
purge_parser = subparsers.add_parser(
    "purge", help="Delete all data from the PostgreSQL database"
)

history_parser.add_argument(
    "-l",
    "--limit",
    help="Return a max of N amount of tasks",
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
    "-w",
    "--watch",
    help="Refresh the output table every S seconds (default = 5)",
    type=int,
    default=5,
    metavar="S",
)
history_parser.add_argument(
    "-v", "--verbose", action="store_true", help="Show all columns from the tasks table"
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


def get_history(verbose: bool):
    query_params = {}

    if args.limit:
        query_params["limit"] = args.limit
        # url += f"?limit={args.limit}"

    if args.status:
        query_params["status"] = args.status

    response = requests.get(f"{API_URL}/history", params=query_params)
    data = response.json()

    for task in data:
        if not verbose:
            print(f"{task['id']}, {task['status']}, {task['result']}")
        else:
            print(
                f"{task['id']}, {task['status']}, {task['result']}, {task['task_type']}, {task['created_at']}"
            )


def get_task_status(id: int):
    response = requests.get(f"{API_URL}/status/{id}")

    if response.status_code == 404:
        print(f"{RED}Error:{RESET} Task {id} does not exist in the database.")
        return

    if response.status_code != 200:
        print(f"{YELLOW}Unexpected error:{RESET} {response.status_code}")
        return

    task = response.json()
    print(f"{task['id']}, {task['status']}, {task['result']}")


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

        time.sleep(0.5)

        status_response = requests.get(f"{API_URL}/status/{task_id}")
        status_data = status_response.json()

        if status_data["status"] == "FAILED":
            error_msg = status_data.get("result", {}).get("error", "Unknown error")
            print(f"{RED}Validation Error:{RESET} {error_msg}")
        else:
            print(f"{GREEN}Success!{RESET} Triggered {task_name}. Task ID: {task_id}")

    except Exception as e:
        print(f"{RED}Error:{RESET} {e}")


# Checking subparser commands
if args.command == "history":
    get_history(args.verbose)

if args.command == "status":
    get_task_status(args.task_id)

if args.command == "trigger":
    trigger_task(args.task_name, args.params)
