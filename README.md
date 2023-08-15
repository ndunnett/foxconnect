
# foxconnect

Web based tool to automatically generate logic flow diagrams for Foxboro I/A series DCS based on configuration files dumped from the ICC.

### Environment

- Windows 11 with WSL2 and Docker Desktop installed
- VSCode with the Remote Development extensions to use dev containers

### Setup

1. Ensure the `icc_git_input` directory containing the configuration files is one directory up from this project.
1. Build the `icc_git_input` volume by running `./build_volume.bat`, this will create a new Docker volume, attach it to a dummy container, then copy the configuration files into the volume.
1. Start the application using `docker-compose` or by opening the project within VSCode in a dev container and running `flask --debug run` inside the container.
1. Access the application in the browser at `127.0.0.1:5000`.
