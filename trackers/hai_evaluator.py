import os

from session_manager import get_session
from util import compute_hash, read_last_hash, write_hash

tracker_name = "hai_evaluator"
product_desc = "HAI Ivy API"
hash_file_path = f"{os.getenv('HASH_DIR', 'hashes')}/{tracker_name}.txt"


def fetch():
    api_url = (
        "https://ai.joinhandshake.com/api/trpc/"
        "task.getAllClaimableTasksForFellow"
        "?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22annotationProjectId%22%3A"
        "%22aebaf7d0-8cc1-4b11-82bc-3a57a2f4ff4f%22%2C%22pipelineStageId%22%3Anull%2C"
        "%22attempters%22%3Anull%2C%22search%22%3Anull%2C%22sortBy%22%3A%22default%22"
        "%2C%22sortOrder%22%3A%22desc%22%2C%22limit%22%3A10%2C%22offset%22%3A0%2C%22"
        "categories%22%3Anull%2C%22priorityLevel%22%3Anull%7D%2C%22meta%22%3A%7B%22"
        "values%22%3A%7B%22pipelineStageId%22%3A%5B%22undefined%22%5D%2C%22attempters"
        "%22%3A%5B%22undefined%22%5D%2C%22search%22%3A%5B%22undefined%22%5D%2C%22cat"
        "egories%22%3A%5B%22undefined%22%5D%2C%22priorityLevel%22%3A%5B%22undefined"
        "%22%5D%7D%2C%22v%22%3A1%7D%7D%7D"
    )
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": (
            "https://ai.joinhandshake.com/fellow/"
            "aebaf7d0-8cc1-4b11-82bc-3a57a2f4ff4f/tasks"
        ),
        "cookie": os.getenv("hai_evaluator_cookie", ""),
    }
    
    session = get_session()
    response = session.get(api_url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()
    else:
        return (
            "error",
            f"Failed to fetch data from API (Status {response.status_code}): ",
            f"Body: {response.text}",
        )


def process(response):
    print(str(response)[:1000] + " truncated...")

    if not response or "error" in str(response):
        return response

    try:
        tasks = response[0]["result"]["data"]["json"].get("tasks") or []
    except (IndexError, KeyError, TypeError, AttributeError) as exc:
        return ("error", "Malformed HAI evaluator response: ", str(exc))

    if not tasks:
        print(f"No claimable tasks in: {product_desc}")
        return ("null", "No changes")

    current_hash = compute_hash(tasks)
    if current_hash != read_last_hash(hash_file_path):
        write_hash(hash_file_path, current_hash)
        print(f"Changes detected in {product_desc}: ", tasks)
        return tasks

    print(f"No changes in {product_desc}")
    return ("null", "No changes")


def template(tasks):
    if "error" in str(tasks):
        return tasks[1] + tasks[2]
    if "null" in tasks:
        return ""
    if not tasks:
        return ""

    return f"{product_desc}: Tasks are available"
