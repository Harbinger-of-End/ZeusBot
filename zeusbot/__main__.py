import os

from zeusbot import ZeusBot

if os.name != "nt":
    from uvloop import install

    install()


def main() -> None:
    zeusbot = ZeusBot()

    zeusbot.run()


if __name__ == "__main__":
    main()
