# FoxConnect

Web based tool to automatically generate logic flow diagrams for Foxboro I/A series DCS based on configuration files dumped from the ICC.

> [!WARNING]
> This app is entirely experimental and an early work in progress, designed for one specific control system and may need to be adapted for others.

## Structure

### Packages

- `packages/app` is the main web application built on [Quart](https://github.com/pallets/quart), broken up into blueprints and extensions detailed in sections below.

- `packages/foxdata` encapsulates the data side of the application, i.e. data models and parsing.

- `packages/pyd3graphviz` serves distribution files from the [d3-graphviz](https://github.com/magjac/d3-graphviz) Node package.

- `packages/pyfastmurmur3` is a thin wrapper around the Rust crate [fastmurmur3](https://crates.io/crates/fastmurmur3), used for fast non-cryptographic string hashing.

- `packages/pyhtmx` serves distribution files from the [HTMX](https://htmx.org/) Node package and provides helper functionality for using HTMX with Python.

- `packages/util` contains various helper functions and utilities not specific to the project.

### Blueprints

- `blocks` has the block detail/diagram views and graphing logic.

- `main` has the main page templates, navigation, error handling, etc.

- `search` has the block search view for querying and filtering blocks from the data source.

### Quart Extensions

- `D3Graphviz` integrates `pyd3graphviz` to serve static files from the Node package.

- `FoxData` integrates `foxdata` for initialising and querying data from the context of a Quart app.

- `Htmx` integrates `pyhtmx` to serve static files from the Node package and inserts HTMX related functionality into the Quart `Request` and `Response` objects.

## Setup

> [!Important]
> Docker is required and the directory containing your ICC configuration files must be accessible locally.

1. Build the `icc_dumps` volume by running `scripts/build_volume.bat` with the path to the directory containing your ICC configuration files as an argument, i.e. `./scripts/build_volume ../icc_dumps`
1. Start the server using `docker-compose up`
1. Access the application in the browser at `127.0.0.1:5000`
