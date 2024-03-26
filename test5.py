import requests
import json
import os
import glob
import argparse
from logzero import logger
from tqdm import tqdm
from datetime import datetime
import time

TIME_STR = datetime.now().strftime("%Y-%m-%d")

BASE_URL = "http://deepcognition.ydns.eu:13910/"
API_KEY = "YHQLVLYZEDNA"

def submit_docs(input_dir):
    files = glob.glob(os.path.join(input_dir, '*.pdf'))

    queue_endpoint = BASE_URL + "api/v1/queue_document/"
    task_id_dict = {}
    for i, filename in enumerate(tqdm(files)):
        with open(filename, 'rb') as f:
            file = {'file': f}
            r = requests.post(queue_endpoint, files=file, data={"access_key": API_KEY, "shipment_id": f"SHIP_{i:>04d}", "doc_type": "transport_invoice", "post_processor": "first", "company": "SuperCargo2", "lang": "Greek + english", "extra_data": '{"Company Name": "Super Logistics LLC", "Branch Name": "Durban", "Department Name": "Export"}'})
            if r.status_code == 200:
                response_data = r.json()
                if response_data.get("status") == "OK":
                    task_id = response_data.get("task_id")
                    task_id_dict[task_id] = response_data.get("file")
                else:
                    logger.warning(f"Failed to submit document '{filename}': {response_data.get('message')}")
            else:
                logger.error(f"Failed to submit document '{filename}': Status Code {r.status_code}, Response: {r.text}")

    with open("temp.json", "w") as f:
        json.dump(task_id_dict, f, indent=4)


def fetch_results(task_id_file, result_dir, max_retries=3, retry_interval=10):
    with open(task_id_file, "r") as f:
        task_id_dict = json.load(f)

    result_endpoint = BASE_URL + "api/v1/fetch_result/"
    result_outdir = os.path.join(result_dir, TIME_STR)
    os.makedirs(result_outdir, exist_ok=True)

    for task_id, filename in task_id_dict.items():
        retries = 0
        while retries < max_retries:
            try:
                r = requests.get(result_endpoint, params={"access_key": API_KEY, "company": "SuperCargo2", "task_id": task_id, "archive": False})
                r.raise_for_status()

                response_data = r.json()
                if response_data.get("status") == "processed":
                    file_outdir = os.path.join(result_outdir, f"{task_id}_{filename.replace('.pdf', '')}")
                    os.makedirs(file_outdir, exist_ok=True)

                    result_file = os.path.join(file_outdir, "results.json")
                    with open(result_file, "w") as f:
                        json.dump(response_data, f, indent=4)

                    logger.info(f"Results for task ID {task_id} saved successfully.")
                    break

                elif response_data.get("status") == "processing":
                    logger.warning(f"Task ID {task_id} is still processing. Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    retries += 1
                    continue

                else:
                    logger.warning(f"Failed to fetch processed results for task ID {task_id}. Status: {response_data.get('status')}")
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch result for task ID: {task_id}. Error: {e}")
                break

            except Exception as ex:
                logger.error(f"An unexpected error occurred while processing task ID {task_id}: {ex}")
                break

        else:
            logger.warning(f"Maximum retries reached for task ID {task_id}. Unable to fetch processed results.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    result_dir = r"C:/Users/argha/Desktop/output/Results"
    input_dir = r"C:/Users/argha/Desktop/input"
    task_id_file = "temp.json"

    parser.add_argument("-do", "--do", required=True, choices=['submit', 'fetch'], type=str.lower, help="Select Task Type")

    args = parser.parse_args()

    if args.do == "submit":
        logger.info(" -----Submitting Docs----")
        submit_docs(input_dir)
    elif args.do == "fetch":
        logger.info(" -----Fetching Result----")
        fetch_results(task_id_file, result_dir)
