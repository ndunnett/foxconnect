from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from utils import yarn_install


class Build(build_py):
    def run(self) -> None:
        """Install node packages using yarn."""
        root_path = Path(__file__).parent.resolve()
        package_path = root_path / "yarn"
        node_modules_link = root_path / "src" / "pyhtmx" / "node_modules"
        yarn_install(package_path, node_modules_link)
        super().run()


setup(
    cmdclass={
        "build_py": Build,
    },
)
