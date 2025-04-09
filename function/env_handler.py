import os


def get_env_paths(key=None):
    HOMEPATH = os.environ.get("HOMEPATH")

    credentials_path = os.getenv(
        "CREDENTIALS_PATH", f"{HOMEPATH}/Documents/GitHub/_CREDENTIAL"
    )
    dmsconnect_folderpath = os.getenv(
        "DMSConnectFolder", f"{HOMEPATH}/Documents/_local_DMSConnectFolder"
    )
    export_root = os.getenv("EXPORT_FOLDER")
    log_root = os.getenv("LOG_ROOT", "log")
    common_lib = os.getenv("LIB_PATH", os.path.join(HOMEPATH, "Documents\lib"))
    paths = {
        "client_config": os.path.join(credentials_path, "client_config.yml"),
        "msgraph_credentials": os.path.join(
            credentials_path, "msgraph_credentials.yml"
        ),
        "Tek_sql_cred": os.path.join(credentials_path, "Tek_sql_cred.yml"),
        "dmsconnectfolder": dmsconnect_folderpath,
        "export_root": export_root,
        "log_root": log_root,
        "common_lib": common_lib,
    }
    if key:
        return paths.get(key, None)
    else:
        return paths
