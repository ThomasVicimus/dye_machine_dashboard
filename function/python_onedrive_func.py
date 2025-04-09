# import json
import requests
import msal
import os
import re
from datetime import datetime
import pytz
import yaml
import io
import json


class ErrorCollector:
    def __init__(self):
        self.error_message = None

    def set_error(self, error_msg):
        self.error_message = error_msg


sharepoint_error_collector = ErrorCollector()


def get_sharepoint_access_token(credentials):
    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.ConfidentialClientApplication(
        credentials["client_id"],
        authority=credentials["authority"],
        client_credential=credentials["secret"],
        # token_cache=...  # Default cache is in memory only.
        # You can learn how to use SerializableTokenCache from
        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )

    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)
    access_token = result["access_token"]
    return access_token


def refresh_token_if_expired(func):
    def wrapper(*args, **kwargs):
        max_retries = 2
        for attempt in range(max_retries):
            result = func(*args, **kwargs)
            if not result == 401:
                return result
            elif result == 401:
                # Get credentials from the original function call

                if "credentials" in kwargs:
                    credentials = kwargs["credentials"]

                else:

                    github_path = os.path.abspath("../")
                    config_path = os.path.join(
                        github_path, "_CREDENTIAL/msgraph_credentials.yml"
                    )
                    with open(config_path, "r") as file:
                        credentials = yaml.safe_load(file)

                if credentials:

                    new_token = get_sharepoint_access_token(credentials["credentials"])

                    # Replace old token in args/kwargs
                    args = list(args)
                    for i, arg in enumerate(args):
                        if isinstance(arg, str) and arg.startswith("eyJ"):
                            args[i] = new_token
                            break
                    args = tuple(args)

                    if "access_token" in kwargs:
                        kwargs["access_token"] = new_token
                    continue
        return result

    return wrapper


@refresh_token_if_expired
def search_sharepoint_site_id(access_token, search):
    endpoint = f"https://graph.microsoft.com/v1.0/sites?search={search}"
    response = requests.get(
        endpoint,
        headers={"Authorization": "Bearer " + access_token},
    )

    if response.status_code == 401:
        return False, response.status_code

    if response.status_code == 200:
        success = True
        response = response.json()
        try:
            site_id = response["value"][0]["id"]
        except IndexError:
            success = False
            site_id = response
        return success, site_id
    else:
        success = False
        print(f"Error: {response.status_code}")
        print(response.json())
        return success, response.status_code


@refresh_token_if_expired
def get_sharepoint_drive_id(access_token, site_id):
    endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    response = requests.get(
        endpoint,
        headers={"Authorization": "Bearer " + access_token},
    )

    if response.status_code == 401:
        return False, response.status_code

    if response.status_code == 200:
        success = True
        response = response.json()
        try:
            drive_id = response["value"][0]["id"]
        except IndexError:
            success = False
            drive_id = response
        return success, drive_id
    else:
        success = False
        print(f"Error: {response.status_code}")
        print(response.json())
        return success, response.status_code


@refresh_token_if_expired
def list_files_in_folder(access_token, drive_id, folder_id=None):
    if not folder_id:
        endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    else:
        endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"

    response = requests.get(
        endpoint,
        headers={"Authorization": "Bearer " + access_token},
    )

    if response.status_code == 401:
        return response.status_code

    if response.status_code == 200:
        files_dict = {
            item["name"]: item["id"] for item in response.json().get("value", [])
        }
        return files_dict
    else:
        print(response.status_code)
        return False


def ms_isfile(filepath):
    filepath = os.path.basename(filepath)
    if re.search(r"\.[\w]*", filepath):
        return True
    else:
        return False


@refresh_token_if_expired
def create_sharepoint_folder(access_token, drive_id, filepath):
    # * clean path
    filepath = filepath.replace("/", "\\")

    if ms_isfile(filepath):
        filename = filepath.split("\\")[-1]
        dirpath = "\\".join(filepath.split("\\")[0:-1])
    else:
        filename = None
        dirpath = filepath

    # *check if the path start on child folder or root folder on sharepoint
    if len(dirpath) == 0 or dirpath == "root":
        # Define the endpoint to get the root folder
        endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root"
        response = requests.get(  # Use token to call downstream service
            endpoint,
            headers={"Authorization": "Bearer " + access_token},
        )
        folder_id = response.json()["id"]
        return folder_id
    else:
        dirs = dirpath.split("\\")

        """get folder id // is not exist Create folder"""
        # Define the endpoint to list the root folders in the drive
        endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"

    # * loop through the path to check and create the non existing folders
    for folder in dirs:
        # Make the request to the Graph API
        response = requests.get(  # Use token to call downstream service
            endpoint,
            headers={"Authorization": "Bearer " + access_token},
        )
        if response.status_code == 401:
            return response.status_code

        elif response.status_code == 200:
            folder_exist = False
            for item in response.json()["value"]:
                if item["name"] == folder:
                    # * folder exist
                    folder_id = item["id"]
                    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
                    folder_exist = True
                    break
            if not folder_exist:
                """folder not exist, CREAT one"""
                # Define the payload for creating the subfolder
                payload = {
                    "name": folder,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "rename",
                }

                # Make the request to create the subfolder
                create_response = requests.post(
                    endpoint,
                    headers={"Authorization": "Bearer " + access_token},
                    json=payload,
                )
                folder_id = create_response.json()["id"]
                endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
                print(f"{folder} created")
    return folder_id


@refresh_token_if_expired
def get_sharepoint_file_id(access_token, drive_id, filepath, enable_create_folder=True):
    """
    get folder_id AND/OR file_id

    For folders:
        - Returns folder_id, None
    For files:
        - Returns parent_folder_id, file_id
    If folder not exist:
        - enable_create_folder == True -> CREATE folder
        - enable_create_folder == False -> return False, False
    If file not exist -> Return None, False
    """

    # * clean path
    filepath = filepath.replace("/", "\\")
    if re.search(r"\\Shared Documents - [\w\s]*", filepath):
        clean_path = re.split(r"\\Shared Documents - [\w\s]*", filepath)[-1]
    elif re.search(r"\\OneDrive - [\w\s]*", filepath):
        """NOT sharepoint \\ personal onedrive instead"""
        clean_path = re.split(r"\\OneDrive - [\w\s]*", filepath)[-1]
    else:
        clean_path = filepath

    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{clean_path}"

    response = requests.get(
        endpoint,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    if response.status_code == 401:
        return response.status_code

    if response.status_code == 404 and not enable_create_folder:
        return False, False

    elif response.status_code == 404 and enable_create_folder:
        folder_id = create_sharepoint_folder(access_token, drive_id, clean_path)

        if ms_isfile(clean_path):
            file_id = False
            info = f"ERROR: a file {filepath} is fed to create_sharepoint_folder. Folder is Created, but the actual file does not exist"
            sharepoint_error_collector.set_error(json.dumps(info))
            json.dumps(info)
        else:
            file_id = None
        return folder_id, file_id

    elif response.status_code == 200:
        item_details = response.json()
        is_folder = True if "folder" in item_details else False

        if is_folder:
            folder_id = item_details["id"]
            file_id = None
        else:
            file_id = item_details["id"]
            # Get parent folder ID
            if "parentReference" in item_details:
                folder_id = item_details["parentReference"].get("id")
            else:
                # If no parent reference, try to get the parent folder ID
                parent_path = "\\".join(clean_path.split("\\")[:-1])
                if parent_path:
                    parent_endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{parent_path}"
                    parent_response = requests.get(
                        parent_endpoint,
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json",
                        },
                    )
                    if parent_response.status_code == 200:
                        folder_id = parent_response.json().get("id")
                    else:
                        folder_id = None
                else:
                    folder_id = None

    return folder_id, file_id


@refresh_token_if_expired
def download_from_sharepoint(access_token, drive_id, source_filepath, des_filepath):
    _, file_id = get_sharepoint_file_id(
        access_token, drive_id, source_filepath, enable_create_folder=False
    )
    if not file_id:
        return False

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    endpoint = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content"
    )
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 401:
        return response.status_code

    if response.status_code == 200:
        des_filepath = os.path.abspath(des_filepath)
        folder = os.path.dirname(des_filepath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(des_filepath, "wb") as file:
            file.write(response.content)
        return des_filepath
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return False


@refresh_token_if_expired
def upload_to_sharepoint(access_token, drive_id, des_folder_id, filepath):
    filepath = os.path.abspath(filepath)
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_content = f.read()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "text/plain"}

    # Define the endpoint to upload the file
    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{des_folder_id}:/{filename}:/content"

    # Make the request to upload the file
    response = requests.put(endpoint, headers=headers, data=file_content, timeout=600)

    # Check if the request was successful
    if response.status_code == 401:
        return response.status_code
    elif response.status_code == 201:
        print("File uploaded successfully")
        uploaded_file = response.json()
        print(f"File ID: {uploaded_file['id']}, File Name: {uploaded_file['name']}")
    elif response.status_code == 200:
        print("File update successfully")
        uploaded_file = response.json()
        print(f"File ID: {uploaded_file['id']}, File Name: {uploaded_file['name']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


@refresh_token_if_expired
def chunk_upload_to_sharepoint(
    access_token, drive_id, des_folder_id, filepath, chunk_size=8 * 1024 * 1024
):
    filepath = os.path.abspath(filepath)
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    # Define the endpoints
    create_upload_session_endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{des_folder_id}:/{filename}:/createUploadSession"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Create upload session
    create_session_response = requests.post(
        create_upload_session_endpoint, headers=headers
    )
    if create_session_response.status_code == 401:
        return create_session_response.status_code

    if create_session_response.status_code != 200:
        print(f"Error creating upload session: {create_session_response.status_code}")
        print(create_session_response.json())
        return

    upload_url = create_session_response.json()["uploadUrl"]

    # Upload file in chunks
    with open(filepath, "rb") as file:
        chunk_number = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break

            start_byte = chunk_number * chunk_size
            end_byte = start_byte + len(chunk) - 1
            content_range = f"bytes {start_byte}-{end_byte}/{file_size}"

            chunk_headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": content_range,
            }

            chunk_response = requests.put(upload_url, headers=chunk_headers, data=chunk)

            if chunk_response.status_code not in [200, 201, 202]:
                print(f"Error uploading chunk: {chunk_response.status_code}")
                print(chunk_response.json())
                return

            chunk_number += 1

            if chunk_response.status_code in [200, 201]:
                # Upload completed
                uploaded_file = chunk_response.json()
                print("File uploaded successfully")
                print(
                    f"File ID: {uploaded_file['id']}, File Name: {uploaded_file['name']}"
                )
                return

    print("File upload completed, but no final response received.")


@refresh_token_if_expired
def check_filesize_and_upload(access_token, drive_id, des_folder_id, filepath):
    file_size = os.path.getsize(filepath)

    # Example size limits (adjust these based on your actual limits)
    SMALL_FILE_LIMIT = 4 * 1024 * 1024  # 4 MB
    MEDIUM_FILE_LIMIT = 1000 * 1024 * 1024  # 1000 MB
    LARGE_FILE_LIMIT = 250 * 1024 * 1024 * 1024  # 250 GB

    if file_size <= SMALL_FILE_LIMIT:
        # Use single request upload
        upload_to_sharepoint(access_token, drive_id, des_folder_id, filepath)
    elif file_size <= MEDIUM_FILE_LIMIT:
        # Use chunked upload
        chunk_upload_to_sharepoint(access_token, drive_id, des_folder_id, filepath)
    else:
        # TODO : Large file upload session
        # Use large file upload session
        # upload_large_file(access_token, drive_id, des_folder_id, filepath)
        print(
            "Large file upload not implemented yet. Medium file size upload implemented for NOW."
        )
        chunk_upload_to_sharepoint(access_token, drive_id, des_folder_id, filepath)


@refresh_token_if_expired
def get_ms_mod_time(access_token, drive_id, file_id):
    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 401:
        return response.status_code

    if response.status_code == 200:
        modified_datetime = response.json().get("lastModifiedDateTime")
        modified_datetime = datetime.fromisoformat(
            modified_datetime.replace("Z", "+00:00")
        )
        local_timezone = pytz.timezone("America/New_York")
        sharepoint_mod_datetime = modified_datetime.astimezone(local_timezone)
        return sharepoint_mod_datetime
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return False


@refresh_token_if_expired
def delete_from_sharepoint(access_token, drive_id, file_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    # Define the endpoint to delete the file
    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"

    # Make the request to delete the file
    response = requests.delete(endpoint, headers=headers)

    if response.status_code == 401:
        return response.status_code

    # Check if the request was successful
    if response.status_code == 204:
        pass
        # print("File deleted successfully")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


@refresh_token_if_expired
def get_file_from_sharepoint(sp_config, var_name, access_token, credentials):
    sp_file_info = sp_config["var"][var_name]
    drive_name = sp_file_info["sharepoint"]
    drive_id = credentials["drive_id"][drive_name]
    sp_path = sp_file_info["path"]
    des_filepath = f"temp_files/{var_name}.xlsx"

    des_filepath = download_from_sharepoint(
        access_token, drive_id, sp_path, des_filepath
    )
    return des_filepath


@refresh_token_if_expired
def delete_if_exist_sharepoint(sp_config, var_name, access_token, credentials):
    sp_file_info = sp_config["var"][var_name]
    drive_name = sp_file_info["sharepoint"]
    drive_id = credentials["drive_id"][drive_name]
    sp_path = sp_file_info["path"]

    _, file_id = get_sharepoint_file_id(
        access_token, drive_id, sp_path, enable_create_folder=False
    )
    if file_id:
        delete_from_sharepoint(access_token, drive_id, file_id)


@refresh_token_if_expired
def download_from_sharepoint_with_ids(access_token, drive_id, file_id, des_filepath):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    endpoint = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content"
    )
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 401:
        return response.status_code

    if response.status_code == 200:
        if not des_filepath:
            return io.BytesIO(response.content)
        else:
            des_filepath = os.path.abspath(des_filepath)
            folder = os.path.dirname(des_filepath)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(des_filepath, "wb") as file:
                file.write(response.content)
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return False
    return des_filepath


@refresh_token_if_expired
def get_updatetime_on_sharepoint_folder(access_token, drive_id, item_id, latest=True):
    """
    Get file information from SharePoint

    Args:
        access_token (str): SharePoint access token
        drive_id (str): Drive ID
        item_id (str): File ID or Folder ID
        latest (bool): When item_id is a folder, True to get latest modified file, False for earliest

    Returns:
        tuple: (filename, file_id, sharepoint_mod_datetime)
    """

    # First, get item details to determine if it's a file or folder
    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
    response = requests.get(
        endpoint,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    if response.status_code == 401:
        return response.status_code

    if response.status_code != 200:
        return None, None, None

    item_details = response.json()
    is_folder = "folder" in item_details

    if not is_folder:
        # If it's a file, simply return its details
        return (
            item_details.get("name"),
            item_details.get("id"),
            item_details.get("lastModifiedDateTime"),
        )

    # If it's a folder, get all files in the folder
    children_endpoint = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children"
    )
    children_response = requests.get(
        children_endpoint,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    if children_response.status_code == 401:
        return children_response.status_code

    if children_response.status_code != 200:
        return None, None, None

    children = children_response.json().get("value", [])

    # Filter out folders, keep only files
    files = [item for item in children if "file" in item]

    if not files:
        return None, None, None

    # Sort files by lastModifiedDateTime
    sorted_files = sorted(
        files,
        key=lambda x: x.get("lastModifiedDateTime", ""),
        reverse=latest,  # True for latest, False for earliest
    )

    # Get the target file (first item after sorting)
    target_file = sorted_files[0]

    return (
        target_file.get("name"),
        target_file.get("id"),
        target_file.get("lastModifiedDateTime"),
    )


@refresh_token_if_expired
def extract_info_from_sp_config(
    access_token,
    credentials,
    sp_config,
    sp_config_path,
    var,
    sharepoint_dealergroup_name,
    sharepoint_path,
):
    # * Create sp_config structure if .yml not exist OR being Blank
    if sp_config is None:
        sp_config = {"var": {}}
        enable_save_sp_config = True
    elif sp_config["var"] == None:
        enable_save_sp_config = True
        sp_config["var"] = {}
    # * Create var if var not in config
    # * Update path if changed
    elif (not var in sp_config["var"]) or (
        sp_config_path != sp_config["var"][var]["path"]
    ):
        enable_save_sp_config = True
    else:
        enable_save_sp_config = False

    if enable_save_sp_config:
        drive_id = credentials["drive_id"][sharepoint_dealergroup_name]
        folder_id, _ = get_sharepoint_file_id(
            access_token, drive_id, sharepoint_path, enable_create_folder=True
        )
        ### save sharepoint info to sp_config
        sp_config["var"][var] = {
            "folder_id": folder_id,
            "path": sharepoint_path,
            "sharepoint": sharepoint_dealergroup_name,
        }
        with open(sp_config_path, "w") as yaml_file:
            yaml.dump(sp_config, yaml_file)

    else:
        drive_id = credentials["drive_id"][sharepoint_dealergroup_name]
        folder_id = sp_config["var"][var]["folder_id"]
    return folder_id, sharepoint_path, sharepoint_dealergroup_name


@refresh_token_if_expired
def upload_log(
    access_token,
    credentials,
    sp_config,
    sp_config_path,
    sharepoint_dealergroup_name,
    log_folder,
):
    drive_id = credentials["drive_id"][sharepoint_dealergroup_name]
    for root, _, files in os.walk(log_folder):
        files = [file for file in files if file.endswith(".log")]
        for file in files:
            var = file
            sharepoint_path = root[root.index("log") :]
            sharepoint_path = sharepoint_path.lstrip("/")
            source_filepath = os.path.join(sharepoint_path, file)
            sharepoint_path = re.sub(r"\d+days_log/", "", sharepoint_path)

            folder_id, sharepoint_path, _ = extract_info_from_sp_config(
                access_token,
                credentials,
                sp_config,
                sp_config_path,
                var,
                sharepoint_dealergroup_name,
                sharepoint_path,
            )

            upload_to_sharepoint(access_token, drive_id, folder_id, source_filepath)
