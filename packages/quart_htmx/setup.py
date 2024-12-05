import subprocess  # noqa: INP001
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class Build(build_py):
    def run(self) -> None:
        """Install node packages using yarn."""

        cwd = Path(__file__).parent.resolve() / "src" / "quart_htmx"
        cmd = '. "$NVM_DIR/nvm.sh"; yes | yarn install'
        subprocess.run(cmd, cwd=cwd, shell=True, check=True)  # noqa: S602
        super().run()


setup(
    cmdclass={
        "build_py": Build,
    },
)
