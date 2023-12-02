import argparse
import importlib
import logging
import os
import platform
import shutil
import subprocess
import sys

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APIDocgen:
    def __init__(self, directory_path):
        self.result_dir = os.path.join(directory_path, "knowl_results")
        self.download_dir = os.path.join(directory_path, "knowl_results/knowl_tools")
        self.django_script_path = os.path.join(
            self.download_dir, "preprocess_django.py"
        )
        self.analyser_path = os.path.join(self.download_dir, "analyser")

    def download_from_link(self, download_url, directory_name, file_path):
        logger.info("Download begins ...")
        logger.info(download_url)

        self.ensure_directory_exists(directory_name)

        response = requests.get(download_url, stream=True)
        with open(file_path, "wb") as file:
            shutil.copyfileobj(response.raw, file)

        os.chmod(file_path, 0o755)

        logger.info("Download ends ...")

    def ensure_file_exists(self, file_path):
        if not os.path.isfile(file_path):
            with open(file_path, "w") as file:
                file.write("--new run--")
            print(f"File created: {file_path}")
        else:
            print(f"File already exists: {file_path}")

    def ensure_directory_exists(self, directory_path):
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)
            print(f"Directory created: {directory_path}")
        else:
            print(f"Directory already exists: {directory_path}")

    def download_github_file(self, local_directory, github_url):
        filename = github_url.split("/")[-1]
        local_path = os.path.join(local_directory, filename)
        response = requests.get(github_url)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"File '{filename}' downloaded successfully.")
        else:
            print(
                f"Failed to download the file. HTTP Status Code: {response.status_code}"
            )
            raise Exception(
                f"Failed to download the django script. HTTP Status Code: {response.status_code}"
            )

    def download_tools(self):
        current_os = get_os()
        print("OS Detected: ", current_os)
        if current_os == "macOS":
            analyser_download_url = f"https://releases.knowl.io/api-docs/python_analyser_mac"
        else:
            analyser_download_url = f"https://releases.knowl.io/api-docs/python_analyser_linux"
        self.download_from_link(
            analyser_download_url, self.download_dir, self.analyser_path
        )

        django_script_download_url = (
            f"https://releases.knowl.io/api-docs/preprocess_django.py"
        )
        self.download_from_link(
            django_script_download_url, self.download_dir, self.django_script_path
        )

def get_os():
    system = platform.system().lower()
    if system == 'darwin':
        return 'macOS'
    elif system == 'linux':
        return 'Linux'
    else:
        return 'Unknown'

def main(directory_path, url_conf, settings_conf, is_local):
    directory_path = os.path.abspath(directory_path)
    docgen = APIDocgen(directory_path)
    docgen.ensure_directory_exists(docgen.result_dir)
    docgen.ensure_directory_exists(docgen.download_dir)
    logger.info("--New Run--")
    logger.info("processing dir: " + directory_path)
    if not is_local:
        logger.info("--getting tools--")
        docgen.download_tools()
    logger.info("--getting endpoints--")

    try:
        sys.path.append(docgen.django_script_path)
        preprocess_django = importlib.import_module("preprocess_django")
    except ImportError:
        raise ImportError(
            "Something went wrong while trying to import the django script. "
        )

    try:
        preprocess_django.main(
            directory_path, docgen.result_dir, url_conf, settings_conf
        )
    except Exception as e:
        error_str = "An error occurred during getting endpoints:\n"
        logger.exception(error_str, e)

    logger.info("--running Python analysers--")
    if is_local:
        py_command = ["python", "python_analyser.py"]
    else:
        py_command = [docgen.analyser_path]
    py_args = [directory_path, docgen.result_dir]
    try:
        binary_process = subprocess.Popen(
            py_command + py_args,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # for line in binary_process.stdout:
        #     logger.info(line.strip())

        # for line in binary_process.stderr:
        #     logger.info(line.strip())

        binary_process.wait()

        if binary_process.returncode == 0:
            logger.info("Python Analyser completed successfully.")
        else:
            logger.error(
                f"Python Analyser failed with return code {binary_process.returncode}."
            )
    except Exception as e:
        error_str = "An error occurred during Python Analyser:\n"
        logger.exception(error_str, e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Knowl Code Docs")
    parser.add_argument("directory", help="Directory path to process.")
    parser.add_argument(
        "-u",
        "--urlconf",
        required=True,
        help="Django url conf.",
    )
    parser.add_argument(
        "-s",
        "--settingsconf",
        required=True,
        help="Django settings conf.",
    )
    parser.add_argument("-l", '--local', action='store_true', default=False)
    args = parser.parse_args()
    directory_path = args.directory
    urlconf = args.urlconf
    settingsconf = args.settingsconf
    is_local = args.local
    main(directory_path, urlconf, settingsconf, is_local)
