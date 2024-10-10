import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build import build as orig_build


class build(orig_build):
    def run(self) -> None:
        """Install node packages using yarn."""

        cwd = Path(__file__).parent.resolve() / "quart_htmx"
        cmd = '. "$NVM_DIR/nvm.sh"; yes | yarn install'
        subprocess.run(cmd, cwd=cwd, shell=True)
        super().run()


setup(
    cmdclass={
        "build": build,
    },
)
