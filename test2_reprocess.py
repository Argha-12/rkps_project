import requests
import json
import os
import glob
import argparse
from logzero import logger
from tqdm import tqdm
from datetime import datetime

TIME_STR = datetime.now().strftime("%Y-%m-%d")  # -TIME-%I%p_%M_%S")
BASE_URL = "http://deepcognition.ydns.eu:13910/"
API_KEY = "YHQLVLYZEDNA"

def submit_docs(input_dir):
    files = glob.glob(input_dir + '/*.pdf')

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


def fetch_results(task_id_file, result_dir):
    task_id_dict = {}
    with open(task_id_file, "r") as f:
        task_id_dict = json.load(f)
    
    result_endpoint = BASE_URL + "api/v1/fetch_result/"

    for task_id, filename in task_id_dict.items():
        try:
            r = requests.get(result_endpoint, params={"access_key": API_KEY, "company": "SuperCargo2", "task_id": task_id, "archive": True})
            r.raise_for_status()

            response_data = r.json()
            if response_data.get("status") == "processed":
                result_outdir = os.path.join(result_dir, TIME_STR)
                os.makedirs(result_outdir, exist_ok=True)

                file_outdir = os.path.join(result_outdir, f"{task_id}_{filename.replace('.pdf', '')}")
                os.makedirs(file_outdir, exist_ok=True)

                result_file = os.path.join(file_outdir, "results.json")
                with open(result_file, "w") as f:
                    json.dump(response_data, f, indent=4)
                
                logger.info(f"{task_id} - {response_data.get('status')}")

                # Download result directory
                result_download_link = response_data.get("result_dir")
                if result_download_link:
                    download_result_dir(result_download_link, file_outdir)
                else:
                    logger.warning(f"No result directory link found for task ID: {task_id}")

            else:
                logger.warning(f"{task_id} - {response_data.get('status')}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch result for task ID: {task_id}. Error: {e}")

        except Exception as ex:
            logger.error(f"An unexpected error occurred while processing task ID {task_id}: {ex}")

def download_result_dir(result_download_link, output_dir):
    logger.info(f"Downloading result directory to {output_dir}")
    try:
        r = requests.get(result_download_link, stream=True)
        r.raise_for_status()

        with open(os.path.join(output_dir, "result_archive.zip"), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download result directory. Error: {e}")

    except Exception as ex:
        logger.error(f"An unexpected error occurred while downloading result directory: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    result_dir = r"C:/Users/argha/Desktop/output/Results"
    input_dir = r"C:/Users/argha/Desktop/input"
    task_id_file = "temp.json"

    parser.add_argument("-do", "--do", required=True, choices=['submit', 'fetch'], type=str.lower, help="Select Task Type")
    print(".........")

    args = parser.parse_args()

    if args.do == "submit":
        logger.info(" -----Submitting Docs----")
        submit_docs(input_dir)
    elif args.do == "fetch":
        logger.info(" -----Fetching Result----")
        fetch_results(task_id_file, result_dir)
