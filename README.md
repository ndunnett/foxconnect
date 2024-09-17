# FoxConnect

Web based tool to automatically generate logic flow diagrams for Foxboro I/A series DCS based on configuration files dumped from the ICC.

> [!WARNING]
> This app is entirely experimental and an early work in progress, designed for one specific control system and may need to be adapted for others.

## Structure

- `src/app` is the main web application built on [`Quart`](https://github.com/pallets/quart), broken up into blueprints:
    - `blocks` has the detail/diagram views and graphing logic
    - `main` has the main page templates, navigation, error handling, etc.
    - `search` has the search/index view
- `src/pyfastmurmur3` is a thin wrapper around the Rust crate [`fastmurmur3`](https://crates.io/crates/fastmurmur3), used for fast non-cryptographic string hashing
- `src/quart_d3graphviz` is a Quart extension to serve the node modules required for [`d3-graphviz`](https://github.com/magjac/d3-graphviz) as static files
- `src/quart_foxdata` is a Quart extension that encapsulates the data side of the application, i.e. parsing, data models, access/querying, etc.

## Setup

> [!Important]
> Docker is required and the directory containing your ICC configuration files must be accessible locally.

1. Build the `icc_dumps` volume by running `./build_volume.bat` with the path to the directory containing your ICC configuration files as an argument, i.e. `./build_volume ../icc_dumps`. This will create a new Docker volume, attach it to a dummy container, copy the configuration files into the volume, then delete the dummy container.
1. Start the server using `docker-compose up` - this will build the project from source and start the production server.
1. Access the application in the browser at `127.0.0.1:5000`.
