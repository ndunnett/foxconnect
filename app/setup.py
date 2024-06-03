from setuptools import Command, Extension, setup
from setuptools.command.build_ext import build_ext as orig_build_ext
from Cython.Build import cythonize
from pathlib import Path
from typing import Generator
import subprocess
import os
import shutil


def install_d3graphviz() -> None:
    """Install d3-graphviz package and setup symbolic links."""
    # setup paths for d3-graphviz module
    project_path = Path(os.getenv("PROJECT_DIR"))
    d3_path = project_path.joinpath("src/app/d3-graphviz")
    modules_path = d3_path / "node_modules"
    static_path = d3_path / "static"

    if not static_path.exists():
        static_path.mkdir(parents=True)

    # install node packages using yarn
    subprocess.run(
        ". \"$NVM_DIR/nvm.sh\"; yes | yarn install",
        cwd=d3_path,
        shell=True
    )

    # relative paths to each file that needs to be linked
    files_to_link = [
        Path("d3/dist/d3.js"),
        Path("d3-graphviz/build/d3-graphviz.js"),
        Path("d3-graphviz/build/d3-graphviz.js.map"),
        Path("@hpcc-js/wasm/dist/graphviz.umd.js"),
        Path("@hpcc-js/wasm/dist/graphviz.umd.js.map"),
    ]

    # setup symbolic links
    for relative_path in files_to_link:
        target = modules_path.joinpath(relative_path)
        link = static_path.joinpath(relative_path.name)

        if not target.is_file():
            raise Exception(f"file doesn't exist: {target}")

        if not link.is_symlink():
            print(f"linking {link} -> {target}")
            link.symlink_to(target)

    print("finished installing d3-graphviz")


class build_ext(orig_build_ext):
    def run(self) -> None:
        super().run()
        install_d3graphviz()


def parse_gitignore(input: str) -> Generator[str, None, None]:
    """Parses contents of a .gitignore file and generates the matched file paths."""
    for line in input.splitlines():
        if s := line.split("#", 1)[0]:
            yield s[1:] if s.startswith("/") else "**/" + s


class clean(Command):
    """Custom command that removes files that match the .gitignore files."""
    description = "Clean project files"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        gitignore_glob = Path(__file__).resolve().parent.glob("**/*.gitignore")

        for path in gitignore_glob:
            with open(path, mode="r") as file:
                patterns = parse_gitignore(file.read())

            for pattern in patterns:
                for m in path.parent.glob(pattern):
                    print(f"removing {m}")

                    try:
                        os.remove(m)
                    except OSError:
                        shutil.rmtree(m, ignore_errors=True)

        print("finished clean")


extensions = [
    Extension("utilities.hashing", ["utilities/hashing/*.pyx"]),
]

cmdclass = {
    "build_ext": build_ext,
    "clean": clean,
}

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3str"}),
    cmdclass=cmdclass,
)
