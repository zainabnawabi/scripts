"""Launch the browser-based cybersecurity awareness quiz."""

from pathlib import Path
import webbrowser


def main() -> None:
    page = Path(__file__).with_name("task_ui.html")
    if not page.is_file():
        raise FileNotFoundError(f"Quiz page not found: {page}")
    if not webbrowser.open(page.resolve().as_uri()):
        raise RuntimeError(
            "Could not open the quiz in a browser. Open task_ui.html manually."
        )


if __name__ == "__main__":
    main()
