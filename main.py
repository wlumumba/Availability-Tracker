from dotenv import load_dotenv
from datetime import datetime
from trackers import macbook_1tb_black, macbook_1tb_silver, fifteenth_street, tesla_model_s, tesla_model_three
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
    print('main.py started', datetime.today())

    trackers = {
        # "macbook_1tb_black": ["fetch", "process", "template"],
        # "macbook_1tb_silver": ["fetch", "process", "template"],
        # "fifteenth_street": ["fetch", "process", "template"],
        # "tesla_model_s": ["fetch", "process", "template"],
        "tesla_model_three": ["fetch", "process", "template"]
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

