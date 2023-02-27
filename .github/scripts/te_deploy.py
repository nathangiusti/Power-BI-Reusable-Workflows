import argparse
import os
from pathlib import Path
import yaml
import urllib.request
import zipfile


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant_id", nargs=1, type=str, required=True)
    parser.add_argument("--files", type=str, nargs=1)
    parser.add_argument("--separator", nargs=1, type=str, default=",")
    parser.add_argument("--db_url", nargs='?', type=str, default=None)
    parser.add_argument("--config", nargs='?', type=str, default=None)
    parser.add_argument("--folder", nargs='?', type=str, default=None)
    parser.add_argument("--roles", nargs=1, type=bool)
    parser.add_argument("--partitions", nargs=1, type=bool)
    parser.add_argument("--te_url", nargs='?', type=str, default=None)
    return parser.parse_args()


def download_te(path, te_url):
    # Download Tabular Editor Portable, extract, and delete zip file
    cwd = os.getcwd()
    zip_location = cwd + path
    urllib.request.urlretrieve(te_url, zip_location)

    with zipfile.ZipFile(zip_location, 'r') as zip_ref:
        zip_ref.extractall(cwd)
    os.remove(zip_location)


def find_updated_datasets(file_list, folder, cfg):
    updated_datasets = {}

    parsed_file_list = []
    for file in file_list:
        file = file.strip()
        path = Path(file)
        # Ignore deleted files
        if os.path.exists(file) and len(path.parts) != 0 and file.endswith(".json") and not file.startswith("."):
            if folder:
                if file.startswith(folder):
                    parsed_file_list.append(file[len(folder):])
            else:
                parsed_file_list.append(file)
        else:
            reason = ""
            if not os.path.exists(file):
                reason += " Does Not Exist | "
            if len(path.parts) == 0:
                reason += " Path too short | "
            if not file.endswith(".json"):
                reason += " Not a .json file | "
            if file.startswith("."):
                reason += " File starts with '.' | "
            print(f"{file} skipped because: {reason}")

    for file in parsed_file_list:
        path = Path(file.strip("/"))
        # If we have a config, create a map from dataset to folder
        if cfg:
            dataset = path.parts[1]
            if not dataset.startswith(".") and dataset not in updated_datasets:
                updated_datasets[dataset] = path.parts[0]
        # If we don't have a config, leave the mapping blank
        else:
            dataset = path.parts[0]
            if not dataset.startswith(".") and dataset not in updated_datasets:
                updated_datasets[dataset] = ""

    return updated_datasets


def main():

    args = parse_arguments()
    tenant_id = args.tenant_id[0]
    db_url = args.db_url if args.db_url and len(args.db_url) > 1 else None
    config = args.config if args.config and len(args.config) > 1 else None
    te_url = args.te_url if args.te_url and len(args.te_url) > 1 else "https://cdn.tabulareditor.com/files/te2/TabularEditor.Portable.zip"

    folder = args.folder if args.folder and len(args.folder) > 1 else ""
    deploy_partition = args.partitions[0]
    deploy_roles = args.roles[0]
    changed_files_list = args.files[0]
    with open(changed_files_list) as f:
        file_names = f.read()
    file_list = file_names.split(args.separator[0])
    
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']

    if client_id is None or client_secret is None:
        raise Exception("CLIENT_ID and CLIENT_SECRET environment variables must be set with credentials")

    if config is None and db_url is None:
        raise Exception("Requires either a config file or a db_url")

    if config is not None and len(config) > 0:
        with open(config, 'r') as yml_file:
            cfg = yaml.safe_load(yml_file)
    else:
        cfg = None

    updated_datasets = find_updated_datasets(file_list, folder, cfg)

    if not updated_datasets:
        print("WARNING: No datasets found. Nothing will be deployed")
        
    # If we need to deploy datasets, download TE
    if updated_datasets:
        download_te("\\TabularEditor.zip", te_url)

    # Post datasets to workspace
    for dataset, workspace_name in updated_datasets.items():
        # If the key is blank, there was no config, so deploy to db_url
        if not workspace_name:
            deploy_url = db_url
        else:
            deploy_url = cfg[workspace_name]
        dataset_loc = (folder + "/" + workspace_name + "/" + dataset).strip("/")
        run_str = "TabularEditor.exe \"{}\" -D \"Provider=MSOLAP;Data Source={};User ID=app:{}@{};Password={}\" \"{}\" -O -C -G -E -W".format(dataset_loc, deploy_url, client_id, tenant_id, client_secret, dataset)
        if deploy_partition:
            run_str = run_str + " -P"
        if deploy_roles:
            run_str = run_str + " -R"
        print("Deploying {} to {}".format(dataset, deploy_url))
        os.system(run_str)
        print("Deployed {} to {}".format(dataset, deploy_url))


if __name__ == "__main__":
    main()
