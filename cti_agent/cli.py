from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

from cti_agent.pipeline import run_pipeline

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command()
def run(
    input: Path | None = typer.Option(None, "--input", "-i"),
    out: Path = typer.Option(Path("out"), "--out", "-o"),
) -> None:
    """Run the CTI pipeline end-to-end (feeds by default)."""
    load_dotenv()
    out.mkdir(parents=True, exist_ok=True)
    result = run_pipeline(out_dir=out, input_path=input)
    console.print(
        f"[green]Done.[/green] Wrote: {result.report_path}, {result.detections_dir}, {result.run_metadata_path}"
    )


if __name__ == "__main__":
    app()

