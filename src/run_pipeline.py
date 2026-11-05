import subprocess
import sys

steps = [
    "src/inspect_data.py",
    "src/validate_data.py",
    "src/export_data.py",
    "src/create_tables.py",
    "src/load_data.py",
    "src/embed_documents.py",
]

for step in steps:
    print(f"\n{'=' * 50}")
    print(f"RUNNING: {step}")
    print("=" * 50)

    result = subprocess.run(
        [sys.executable, step],
        check=False
    )

    if result.returncode != 0:
        print(f"\nPIPELINE FAILED AT: {step}")
        sys.exit(result.returncode)

print("\nALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")