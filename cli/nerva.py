import requests
import argparse


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

status_parser.add_argument(
    "task_id", help="The numerical ID of the task", type=int, metavar="ID"
)


args = parser.parse_args()


def get_history():
    query_params = {}

    if args.limit:
        query_params["limit"] = args.limit
        # url += f"?limit={args.limit}"

    if args.status:
        query_params["status"] = args.status

    response = requests.get(f"{API_URL}/history", params=query_params)
    data = response.json()

    for task in data:
        print(f"{task['id']}, {task['status']}, {task['result']}")


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


# Checking subparser commands
if args.command == "history":
    get_history()

if args.command == "status":
    get_task_status(args.task_id)
