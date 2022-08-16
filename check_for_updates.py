from __future__ import annotations

from publishers.ms.edge import MicrosoftEdge

component_list = [MicrosoftEdge]


def main() -> None:
    for cls in component_list:
        comp = cls()
        comp.check_for_updates()


if __name__ == "__main__":
    main()
