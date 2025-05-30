import subprocess
import uvicorn

def run_pytest():
    # Run pytest with the --disable-warnings flag
    result = subprocess.run(["pytest", "--disable-warnings"], capture_output=True, text=True)

if __name__ == "__main__":
    run_pytest()