from pathlib import Path

from bs4 import BeautifulSoup

cwd_path = Path().cwd() / "data" / "raw"
file_path = cwd_path / "index.html"

with file_path.open("r") as f:
    raw_html = f.read()

soup = BeautifulSoup(raw_html, "html.parser")


def main(html: BeautifulSoup = soup) -> None:
    for item in html.find_all("a", class_="hoverinfo_trigger"):
        print(item)


if __name__ == "__main__":
    main()
