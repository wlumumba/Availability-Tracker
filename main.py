from dotenv import load_dotenv
import macbook_512
import email_service

def run_tracker(tracker_module, functions):
    result = None
    for function in functions:
        func = getattr(tracker_module, function)
        if function == "fetch":
            result = func()
        else:
            result = func(result)
    return result

def main():
    load_dotenv()

    trackers = {
        "macbook_512": ["fetch", "process", "template"]
    }

    final_templates = {}
    for tracker_name, functions in trackers.items():
        tracker_module = globals()[tracker_name]
        result = run_tracker(tracker_module, functions)
        final_templates[tracker_name] = result

    # Send results to email_service
    email_service.send_email(final_templates)

if __name__ == "__main__":
    main()

