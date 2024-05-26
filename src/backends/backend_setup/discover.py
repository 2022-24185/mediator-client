
import sys
import os
import subprocess

def _get_path(executable_name) -> str:
    """finds full path of an executable on the system PATH"""
    if sys.platform == 'win32' and not executable_name.lower().endswith('.exe'):
        executable_name += '.exe'
    path_dirs = os.environ['PATH'].split(os.pathsep)
    for path_dir in path_dirs:
        executable_path = os.path.join(path_dir, executable_name)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path
    return ""


def get_chrome_path() -> str:
    chrome = ''
    if not chrome:
        chrome = _get_path('chrome')
    if not chrome:
        chrome = _get_path('google-chrome')
    if not chrome:
        print("Error: No Chrome executable path set and no Chrome executable found on system PATH")
        sys.exit(1)
    return chrome


def get_chrome_version(path = None) -> str:
    if path is None: path = get_chrome_path()
    try:
        result = subprocess.run(path + ' --version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if line.startswith('Google Chrome'):
                    version = line.split()[2]
                    return version
        else:
            error_message = result.stderr.strip()
            print(f"Error: {error_message}")
    except FileNotFoundError:
        print("Google Chrome not found on the PATH.")
    return None  # Chrome version not found
