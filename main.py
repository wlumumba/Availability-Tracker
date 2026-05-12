import argparse
import importlib
import sys
from dotenv import load_dotenv
from datetime import datetime
import email_service

TRACKER_MODULE_PATHS = {
    "tesla_model_s": "trackers.tesla_model_s",
    "tesla_model_three": "trackers.tesla_model_three",
    "sheridan": "trackers.sheridan",
    "hai_evaluator": "trackers.hai_evaluator",
}

TRACKER_PIPELINES = {
    # "macbook_1tb_black": ["fetch", "process", "template"],
    # "macbook_1tb_silver": ["fetch", "process", "template"],
    # "fifteenth_street": ["fetch", "process", "template"],
    # "tesla_model_s": ["fetch", "process", "template"],
    # "tesla_model_three": ["fetch", "process", "template"],
    "sheridan": ["fetch", "process", "template"],
    "hai_evaluator": ["fetch", "process", "template"],
}


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

    # Send results to email_service
    email_service.send_email(final_templates)

if __name__ == "__main__":
    main()
