import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_DIR  = BASE_DIR / "app"
SRC_DIR  = BASE_DIR / "src"
RAW_DIR  = BASE_DIR / "data" / "raw"

def run(label: str, cmd: list, cwd: Path = None) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=str(cwd or BASE_DIR))
    if result.returncode != 0:
        print(f"\n[ERROR] Step failed: {label}")
        print("Fix the error above and re-run main.py")
        sys.exit(1)
    print(f"[OK] {label} completed successfully.")

def main() -> None:
    print("\nIPL Analytics Dashboard — Setup & Launch")
    print("=========================================\n")

    # Step 1 — Download raw data
    raw_script = RAW_DIR / "rawdatadownload.py"
    if not raw_script.exists():
        print(f"[ERROR] Could not find: {raw_script}")
        sys.exit(1)

    ipl_csv = RAW_DIR / "IPL.csv"
    if ipl_csv.exists():
        skip = input("\nIPL.csv already exists. Skip download? [Y/n]: ").strip().lower()
        if skip in ("", "y", "yes"):
            print("[SKIP] Using existing IPL.csv")
        else:
            run("Downloading raw data from Kaggle", [sys.executable, str(raw_script)], cwd=RAW_DIR)
    else:
        run("Downloading raw data from Kaggle", [sys.executable, str(raw_script)], cwd=RAW_DIR)

    # Step 2 — Run data processing
    processing_script = SRC_DIR / "data_processing.py"
    if not processing_script.exists():
        print(f"[ERROR] Could not find: {processing_script}")
        sys.exit(1)

    run("Processing data and generating CSVs", [sys.executable, str(processing_script)], cwd=SRC_DIR)

    # Step 3 — Launch Streamlit
    home = APP_DIR / "Home.py"
    if not home.exists():
        print(f"[ERROR] Could not find: {home}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print("  Launching Dashboard")
    print(f"{'='*50}")
    print("Opening at http://localhost:8501")
    print("Press Ctrl+C to stop.\n")

    subprocess.run(
        ["streamlit", "run", str(home)],
        cwd=str(APP_DIR)
    )

if __name__ == "__main__":
    main()