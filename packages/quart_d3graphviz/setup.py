import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class Build(build_py):
    def run(self) -> None:
        """Install node packages using yarn."""

        cwd = Path(__file__).parent.resolve() / "src" / "quart_d3graphviz"
        cmd = '. "$NVM_DIR/nvm.sh"; yes | yarn install'
        subprocess.run(cmd, cwd=cwd, shell=True)
        super().run()


setup(
    cmdclass={
        "build_py": Build,
    },
)
