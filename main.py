from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from cti_agent.pipeline import run_pipeline


def main() -> int:
    """
    Simple entrypoint to run the workflow start-to-finish.

    - Pulls from configured feeds by default
    - Optionally appends a local bulletin file if provided
    - Writes outputs into ./out
    """
    load_dotenv()
    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Optional local bulletin (kept simple: drop a file at examples/sample_bulletin.txt if desired)
    local_input = Path("examples/sample_bulletin.txt")
    input_path = local_input if local_input.exists() else None

    result = run_pipeline(out_dir=out_dir, input_path=input_path)
    print(f"Wrote report: {result.report_path}")
    print(f"Wrote detections: {result.detections_dir}")
    print(f"Wrote metadata: {result.run_metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

