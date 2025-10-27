'''
can be used as:
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/basu-10/installers/main/installer_termtools.py').Content | python -

The install_termtools.py script is a complete installer that downloads, installs, and configures TermTools for Windows with right-click context menu integration.

Installs TermTools from GitHub to Program Files and sets up context menu.
Run once as Administrator.

'''


'''
flowchart TD
    A[Start Script] --> B{Check Admin Privileges}
    B -->|Not Admin| C[Re-launch with Admin Rights]
    C --> D[Exit Current Process]
    B -->|Is Admin| E[Initialize Variables]
    
    E --> F[Create Temp Directory]
    F --> G[Download ZIP from GitHub]
    G --> H[Extract ZIP to Temp]
    
    H --> I[Create Target Directory Structure]
    I --> J{Target Directory Exists?}
    J -->|Yes| K[Remove Existing Directory]
    J -->|No| L[Create New Directory]
    K --> L
    
    L --> M[Copy All Files from Extract to Target]
    M --> N[Print Installation Success]
    
    N --> O[Setup Context Menu]
    O --> P{add_to_context_menu.py exists?}
    P -->|Yes| Q[Run Context Menu Setup]
    P -->|No| R[Skip Context Menu Setup]
    
    Q --> S[Context Menu Script Checks Admin]
    S --> T[Create Registry Entries]
    T --> U[Set Menu Text: 'Run TermTools']
    U --> V[Set Command Path]
    
    V --> W[Cleanup Temp Directory]
    R --> W
    W --> X[End Script]
    
'''

import os, shutil, tempfile, zipfile, urllib.request, subprocess
import ctypes, sys

# Check for admin privileges and re-run with elevation if needed
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

REPO = "basu-10/termtools"     # e.g. "user/repo"
BRANCH = "main"
TARGET_BASE = "BasusTools"
TARGET_APP = "TermTools"

program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
tempdir = tempfile.mkdtemp(prefix="gh_install_")

try:
    zip_path = os.path.join(tempdir, "repo.zip")
    url = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
    print("Downloading", url)
    urllib.request.urlretrieve(url, zip_path)

    extract_dir = os.path.join(tempdir, "extract")
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_dir)
    print("Extracted to", extract_dir)

    root = next(os.scandir(extract_dir)).path

    # Create the target directory structure: BasusTools/TermTools
    target_base = os.path.join(program_files, TARGET_BASE)
    target_app = os.path.join(target_base, TARGET_APP)
    
    if os.path.exists(target_app):
        shutil.rmtree(target_app, ignore_errors=True)
    os.makedirs(target_app, exist_ok=True)
    
    # Copy all files to the TermTools subdirectory
    for item in os.listdir(root):
        s = os.path.join(root, item)
        d = os.path.join(target_app, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print(f"Installed to {target_app}.")

    print("Setting up context menu...")
    # run add_to_context_menu.py if found
    py = os.path.join(target_app, "add_to_context_menu.py")
    if os.path.exists(py):
        subprocess.run(["python", py], check=False)

finally:
    print("Cleaning up...")
    shutil.rmtree(tempdir, ignore_errors=True)
