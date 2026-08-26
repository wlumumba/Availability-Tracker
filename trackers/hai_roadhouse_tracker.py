import os
from datetime import datetime

from tenacity import retry, retry_if_result, stop_after_attempt, wait_exponential

from session_manager import get_session
from util import compute_hash, read_last_hash, write_hash

tracker_name = "hai_roadhouse_tracker"
product_desc = "HAI Roadhouse"
hash_file_path = f"{os.getenv('HASH_DIR', 'hashes')}/{tracker_name}.txt"
MAX_RETRIES = 3


def _is_503(response):
    return response.status_code == 503


def _print_retry(retry_state):
    delay = retry_state.next_action.sleep
    retry_number = retry_state.attempt_number
    print(
        f"{product_desc}: received 503; "
        f"retrying {retry_number}/{MAX_RETRIES} in {delay:g}s",
        flush=True,
    )


@retry(
    retry=retry_if_result(_is_503),
    stop=stop_after_attempt(MAX_RETRIES + 1),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=_print_retry,
    retry_error_callback=lambda state: state.outcome.result(),
)
def _get_roadhouse_response(session, api_url, headers):
    return session.get(api_url, headers=headers, timeout=20)


def fetch():
    api_url = (
        "https://ai.joinhandshake.com/api/trpc/"
        "task.getAllClaimableTasksForFellow"
        "?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22annotationProjectId%22%3A"
        "%225df1908e-d347-46ae-b522-2bd363b7477a%22%2C%22pipelineStageId%22%3Anull%2C"
        "%22attempters%22%3Anull%2C%22search%22%3Anull%2C%22sortBy%22%3A%22default%22"
        "%2C%22sortOrder%22%3A%22desc%22%2C%22limit%22%3A100%2C%22offset%22%3A0%2C%22"
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
                "84828944-4139-4c17-8166-2a562f835eb0/tasks"
            ),
            "cookie": os.getenv("hai_equator_track_cookie", os.getenv("hai_evaluator_cookie", "")),
        }

    try:
        session = get_session()
        response = _get_roadhouse_response(session, api_url, headers)
        if response.status_code == 200:
            return response.json()

        return (
            "failure",
            f"Roadhouse API failed to fetch data (Status {response.status_code}) ",
            f"body: {response.text}",
        )
    except Exception as exc:
        return ("failure", "Roadhouse API fetch error: ", str(exc))


def process(response):
    print(str(response)[:1000] + " truncated...")

    if not response or (type(response) == tuple and "failure" in response[0]):
        return response

    try:
        tasks = response[0]["result"]["data"]["json"].get("tasks") or []

        if not tasks:
            print(f"No claimable tasks in: {product_desc}")
            return ("null", "No changes")

        print(f"Fetched {len(tasks)} tasks")

        now = datetime.now()
        current_hash = compute_hash(
            {
                "task_count": len(tasks[:10]),
                "date": now.strftime("%Y-%m-%d"),
                "hour": now.hour,
                "half_hour_bucket": now.minute // 30,
                "quarter_hour_bucket": now.minute // 15,
            }
        )
        if current_hash != read_last_hash(hash_file_path):
            write_hash(hash_file_path, current_hash)
            print(f"Changes detected in {product_desc}")
            return tasks

        print(f"No changes in {product_desc}")
        return ("null", "No changes")
    except Exception as exc:
        return ("failure", "Process step error: ", str(exc))


def template(tasks):
    if type(tasks) == tuple and "failure" in tasks[0]:
        return tasks[1] + tasks[2]
    if type(tasks) == tuple and "null" in tasks:
        return ""
    if not tasks:
        return ""

    return f"{product_desc}: {len(tasks)} tasks are available"
