import os, shutil, tempfile, zipfile, urllib.request, subprocess

REPO = "basu-10/termtools"     # e.g. "user/repo"
BRANCH = "main"
TARGETS = ["BasusTools", "TermTools"]

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

    for t in TARGETS:
        target = os.path.join(program_files, t)
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
        os.makedirs(target)
        for item in os.listdir(root):
            s = os.path.join(root, item)
            d = os.path.join(target, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    print("Installed to Program Files.")

    print("Setting up context menu...")
    # run add_to_context_menu.py if found
    for t in TARGETS:
        py = os.path.join(program_files, t, "add_to_context_menu.py")
        if os.path.exists(py):
            subprocess.run(["python", py], check=False)
            break

finally:
    print("Cleaning up...")
    shutil.rmtree(tempdir, ignore_errors=True)
