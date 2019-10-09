import os

UTILS_PATH = os.path.abspath(__file__).replace("/get_paths.py", "")
ROOT_PATH = UTILS_PATH.replace("/utils", "")
PDF_PATH = os.path.join(ROOT_PATH, "pdf_files")
