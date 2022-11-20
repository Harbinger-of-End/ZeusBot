import os
from shutil import rmtree


def main() -> None:
    root = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
    )

    for path, dirnames, _ in os.walk(root):
        for dirname in dirnames:
            if dirname == "__pycache__":
                rmtree(os.path.join(path, dirname))


if __name__ == "__main__":
    main()
