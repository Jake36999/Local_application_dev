import json
from pathlib import Path

# Utility logging function
def log(msg):
    print(msg)

class BackendOrchestrator:
    def __init__(self):
        self.root = Path(__file__).parent.resolve()

    def step_verify_constitution(self):
        log("--- CONSTITUTIONAL CHECK ---")
        meth_path = self.root / "methodology_library.json"
        if not meth_path.exists():
            log("⚠️ Constitution missing (methodology_library.json)")
            return

        with open(meth_path, "r", encoding="utf-8") as f:
            constitution = json.load(f)
        
        # Zombie Check: Ensure no deprecated assets exist
        zombies_found = []
        for asset in constitution.get("deprecated_assets", []):
            clean_path = asset.split(" ")[0]
            if (self.root / clean_path).exists():
                zombies_found.append(clean_path)
        
        if zombies_found:
            log(f"❌ VIOLATION: Found deprecated assets: {zombies_found}")
            print("RECOMMENDATION: Run cleanup_legacy.ps1 immediately.")
        else:
            log("✅ System is Constitutionally Compliant (No Zombies Found).")

    def run(self):
        self.step_verify_constitution()
        log("Orchestrator boot sequence complete.")

if __name__ == "__main__":
    BackendOrchestrator().run()
