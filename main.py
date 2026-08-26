import argparse
import importlib
import os
import re
import sys
from dotenv import load_dotenv
from datetime import datetime
from service import discord_service, email_service, pushover_service

TRACKER_MODULE_PATHS = {
    "sheridan": "trackers.sheridan",
    "hai_ivy_track": "trackers.hai_ivy_track",
    "hai_roadhouse_tracker": "trackers.hai_roadhouse_tracker",
    "hai_equator_track": "trackers.hai_equator_track",
}

TRACKER_PIPELINES = {
    "sheridan": ["fetch", "process", "template"],
    "hai_ivy_track": ["fetch", "process", "template"],
    "hai_roadhouse_tracker": ["fetch", "process", "template"],
    "hai_equator_track": ["fetch", "process", "template"],
}

DISCORD_ALIAS_PATTERN = re.compile(r"[A-Z0-9_]+")


def run_tracker(tracker_module, functions):
    result = None
    for function in functions:
        func = getattr(tracker_module, function)
        if function == "fetch":
            result = func()
        else:
            result = func(result)
    return result


def parse_args():
    parser = argparse.ArgumentParser(description="Run availability trackers.")
    parser.add_argument(
        "tracker_name",
        nargs="?",
        help="Optional tracker name to run by itself.",
    )
    return parser.parse_args()


def get_trackers_to_run(tracker_name=None):
    if not tracker_name:
        return TRACKER_PIPELINES

    if tracker_name not in TRACKER_MODULE_PATHS:
        available_trackers = ", ".join(sorted(TRACKER_MODULE_PATHS))
        raise ValueError(
            f"Unknown tracker '{tracker_name}'. Available trackers: {available_trackers}"
        )

    if tracker_name not in TRACKER_PIPELINES:
        raise ValueError(
            f"Tracker '{tracker_name}' exists but is not enabled in TRACKER_PIPELINES."
        )

    return {tracker_name: TRACKER_PIPELINES[tracker_name]}


def load_tracker_module(tracker_name):
    return importlib.import_module(TRACKER_MODULE_PATHS[tracker_name])


def parse_discord_routes(raw_routes):
    routes = {}
    if not raw_routes.strip():
        return routes

    for entry in raw_routes.split(","):
        entry = entry.strip()
        if entry.count("=") != 1:
            raise ValueError(f"malformed route '{entry}' (expected TRACKER=CHANNEL)")

        tracker_name, channel_alias = (part.strip() for part in entry.split("=", 1))
        if not tracker_name or not channel_alias:
            raise ValueError(f"malformed route '{entry}' (expected TRACKER=CHANNEL)")
        if tracker_name in routes:
            raise ValueError(f"duplicate route for tracker '{tracker_name}'")
        if tracker_name not in TRACKER_MODULE_PATHS:
            raise ValueError(f"unknown tracker '{tracker_name}'")
        if not DISCORD_ALIAS_PATTERN.fullmatch(channel_alias):
            raise ValueError(
                f"invalid channel alias '{channel_alias}' "
                "(use uppercase letters, numbers, and underscores)"
            )
        routes[tracker_name] = channel_alias

    return routes


def send_notifications(data):
    routes = parse_discord_routes(os.getenv("DISCORD_ROUTES", ""))
    pushover_data = {
        tracker_name: message
        for tracker_name, message in data.items()
        if tracker_name not in routes
    }
    discord_data = {}
    for tracker_name, message in data.items():
        if tracker_name in routes:
            discord_data.setdefault(routes[tracker_name], {})[tracker_name] = message

    if pushover_data:
        pushover_service.send_notifications(pushover_data)
    for channel_alias, messages in discord_data.items():
        webhook_url = os.getenv(f"DISCORD_WEBHOOK_{channel_alias}")
        if not webhook_url:
            tracker_names = ", ".join(messages)
            print(
                f"Discord webhook is missing for {channel_alias}; "
                f"dropping notifications for: {tracker_names}"
            )
            continue
        discord_service.send_notifications(messages, webhook_url, channel_alias)


def main():
    args = parse_args()
    load_dotenv()
    print("main.py started", datetime.today())

    try:
        trackers = get_trackers_to_run(args.tracker_name)
    except ValueError as exc:
        print(exc)
        sys.exit(2)

    final_templates = {}
    for tracker_name, functions in trackers.items():
        tracker_module = load_tracker_module(tracker_name)
        result = run_tracker(tracker_module, functions)
        final_templates[tracker_name] = result

    # V1: Send results to email_service
    # email_service.send_email(final_templates)

    try:
        send_notifications(final_templates)
    except ValueError as exc:
        print(f"Invalid DISCORD_ROUTES: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
