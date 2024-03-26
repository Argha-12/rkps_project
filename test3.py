import requests
import json
import os
import glob
import argparse
from logzero import logger
from tqdm import tqdm
from datetime import datetime
TIME_STR = datetime.now().strftime("%Y-%m-%d")#-TIME-%I%p_%M_%S")


BASE_URL = "http://deepcognition.ydns.eu:13910/"
API_KEY = "YHQLVLYZEDNA"

def submit_docs(input_dir):
    files = glob.glob(input_dir+'/*.pdf')

    queue_endpoint = BASE_URL + "api/v1/queue_document/"
    task_id_dict = {}
    for i,filename in enumerate(tqdm(files)):
        f = open(filename, 'rb')
        file = {'file': f}
        r = requests.post(queue_endpoint, files=file, data={"access_key": API_KEY, "shipment_id":f"SHIP_{i:>04d}", "doc_type": "transport_invoice", "post_processor": "first", "company": "SuperCargo2", "lang": "Greek + english" , "extra_data" : '{"Company Name" : "Super Logistics LLC", "Branch Name" : "Durban", "Department Name": "Export"}'})
        if r.status_code == 200:
            respone_data = r.json()
            if respone_data.get("status") == "OK":
                task_id = respone_data.get("task_id")
                task_id_dict[task_id] = respone_data.get("file")
            else:
                logger.warning(respone_data)
        else:
            logger.error(r.text)
    
    with open("temp.json","w") as f:
        json.dump(task_id_dict,f, indent=4)


def fetch_results(task_id_file,result_dir):
    task_id_dict = {}
    with open (task_id_file,"r") as f:
        task_id_dict = json.load(f)
    result_endpoint = BASE_URL + "api/v1/fetch_result/"
    result_outdir = os.path.join(result_dir,TIME_STR)
    os.makedirs(result_outdir,exist_ok=True)
    for task_id,filename in task_id_dict.items():
        r = requests.get(result_endpoint, params={"access_key": API_KEY, "company": "SuperCargo2", "task_id": task_id, "archive" : False})
        if r.status_code == 200:
            respone_data = r.json()
            print(respone_data)
            if respone_data.get("status") in ["processed"] :
            
                file_outdir = os.path.join(result_outdir, f"{task_id}_{filename.replace('.pdf','')}")
                os.makedirs(file_outdir,exist_ok=True)

                result_file = os.path.join(file_outdir,"results.json")
                with open(result_file, "w") as f:
                    json.dump(respone_data, f, indent=4)
                logger.info(f"{task_id} - {respone_data.get('status')}")
                # print(respone_data)

            else:
                logger.warning(f"{task_id} - {respone_data.get('status')}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    result_dir=r"C:/Users/argha/Desktop/output/Results"
    input_dir=r"C:/Users/argha/Desktop/input"
    task_id_file = "temp.json"


    parser.add_argument("-do", "--do", required=True, choices=['submit','fetch'],type=str.lower,help="Select Task Type")
    print(".........")

    args = parser.parse_args()

    if args.do == "submit":
        logger.info(" -----Submitting Docs----")
        submit_docs(input_dir)
    if args.do == "fetch":
        logger.info(" -----Fetching Result----")
        fetch_results(task_id_file, result_dir)   

