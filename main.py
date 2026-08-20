"""Small command-line entry point for TechMind."""

from techmind.config import get_paths

if __name__ == "__main__":
    paths = get_paths()
    print(f"[TechMind] Project root: {paths.root}")
    print("[TechMind] Run notebooks 01 → 05 in order to build the pipeline.")
