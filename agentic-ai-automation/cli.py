"""Command-line interface for running agents without the HTTP server."""
import argparse
import asyncio

from agents import Orchestrator


async def _run(command: str) -> None:
    orch = Orchestrator()
    await orch.store.init()
    if command == "triage":
        print(await orch.run_full_triage())
    elif command == "reminders":
        print(await orch.run_reminders())
    elif command == "stats":
        print(await orch.store.stats())


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic AI Automation CLI")
    parser.add_argument(
        "command", choices=["triage", "reminders", "stats"], help="Action to run"
    )
    args = parser.parse_args()
    asyncio.run(_run(args.command))


if __name__ == "__main__":
    main()
