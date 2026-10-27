import subprocess, sys, os, time, yaml, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
APP = cfg["app_repo"]
PKG = cfg["package"]
ACT = cfg["activity"]
APK = os.path.join(APP, cfg["apk"])
SMOKE = cfg["smoke_seconds"]

def run(cmd, cwd=None, check=True):
    print(">", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd)
    if check and r.returncode != 0:
        raise SystemExit(f"Command failed: {cmd}")
    return r.returncode

def main():
    os.chdir(APP)
    run(["flutter", "pub", "get"])
    run(["flutter", "test"], check=False)
    run(["flutter", "build", "apk", "--release"])
    if not os.path.exists(APK):
        raise SystemExit("APK missing")

    dev = cfg.get("device_serial") or ""
    adb = ["adb"] + (["-s", dev] if dev else [])
    run(adb + ["devices"])
    run(adb + ["install", "-r", APK])
    run(adb + ["logcat", "-c"])
    run(adb + ["shell", "am", "start", "-n", ACT])
    time.sleep(SMOKE)
    subprocess.run(adb + ["exec-out", "screencap", "-p"], stdout=open(os.path.join(ROOT, "screenshot.png"), "wb"))
    log = subprocess.run(adb + ["logcat", "-d"], capture_output=True, text=True).stdout
    open(os.path.join(ROOT, "logcat.txt"), "w").write(log)
    # crash detection simple
    crashes = [l for l in log.splitlines() if "FATAL EXCEPTION" in l or "ANR" in l]
    report = {"crashes": crashes, "log_lines": len(log.splitlines())}
    json.dump(report, open(os.path.join(ROOT, "report.json"), "w"), indent=2)
    print("CRASHES:", len(crashes))
    if crashes:
        raise SystemExit("Crashes detected")
    print("QA OK")

if __name__ == "__main__":
    main()
