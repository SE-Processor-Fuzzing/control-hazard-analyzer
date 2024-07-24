# Control hazard analyzer

<p align="center">
<a href="https://github.com/osogi/control-hazard-analyzer/actions"><img alt="Lint" src="https://github.com/SE-Processor-Fuzzing/control-hazard-analyzer/actions/workflows/checks.yml/badge.svg"></a>
<a href="https://github.com/osogi/control-hazard-analyzer/actions"><img alt="Test" src="https://github.com/SE-Processor-Fuzzing/control-hazard-analyzer/actions/workflows/test.yml/badge.svg"></a>
<a href="https://github.com/osogi/control-hazard-analyzer/blob/main/LICENSE.md"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<img alt="GitHub all releases" src="https://img.shields.io/github/downloads/osogi/control-hazard-analyzer/total">
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<img alt="GitHub commit activity (branch)" src="https://img.shields.io/github/commit-activity/m/osogi/control-hazard-analyzer">
</p>

**Control hazard analyzer** *(abbreviated `cha.py`)* is toolchain for analyzing control hazards. Toolchain consists of
three steps: test generation in C, test profiling using a profiler (perf, gem5 simulator), and result collection.

---

## Requirements

- Python 3.10+
- gem5 (optional)

## Installation

Clone the repository

```bash
git clone --recurse-submodules https://github.com/SE-Processor-Fuzzing/control-hazard-analyzer.git
```

### gem5

For using gemProofiler one needs to have gem5 and library M5ops:
- [gem5 installation](https://www.gem5.org/getting_started/)
- [M5ops installation](https://www.gem5.org/documentation/general_docs/m5ops/)

They can be installed manually or using `thirdparty/gem5` submodule.

```bash
python3 ./scripts/install_gem5.py X86 opt ./thirdparty/gem5/build_cache
```

> [!TIP]
> It is possible to configure ISA, build variant and build cache directory for gem5 installation.
> For more information run `python ./scripts/install_gem5.py --help`

### cha.py dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Toolchain structure

- [aggregate](#aggregate) - toolchain driver
- [generate](#generate) - test generate
- [analyze](#analyze) - execute and profile tests
- [summarize](#summarize) - give statistics on analyzed files

### aggregate

**Usage example:**

```bash
python3 cha.py aggregate
```

Example result:
![example_of_output](https://github.com/osogi/control-hazard-analyzer/assets/66139162/5cb43919-ba4e-47cf-b675-79eec8d33e3c)


Also, you can pass many options to utilities, see help for more details

To read more about `aggreagte` visit [Docs](docs/usage/Aggregate.md)

```bash
python3 cha.py aggregate --help
```

### generate

**Usage example:**

```bash
python3 cha.py generate --repeats=10 --out-dir="out" --log-level DEBUG
```

To read more about `generate` visit [Docs](docs/usage/Generate.md)

### analyze

**Usage example:**

```bash
python3 cha.py analyze --test-dir="out" --out-dir="perf_result" --log-level DEBUG
```

To read more about `analyze` visit [Docs](docs/usage/Analyze.md)

### summarize

**Usage example:**

```bash
python3 cha.py summarize --src-dirs="perf_result" --out-dir="summarize_result" --log-level DEBUG
```

To read more about `summarize` visit [Docs](docs/usage/Summarize.md)

### Multi-command Execution
You can pass multiple commands in a single run. This allows you to combine multiple steps into one command sequence

**Usage example:**
```bash
python3 cha.py generate --out-dir="tests" analyze --test-dir="tests" --out-dir="results" summarize --src-dirs="results" --out-dir="summarize_result"
```

## Development

### Requirements

```bash
python3 -m pip install -r requirements.dev.txt
```

### Pre-commit

#### Install pre-commit-hooks

```bash
pre-commit install
```

#### Run manually

```bash
pre-commit run --all-files --color always --verbose
```
## Troubleshooting

### Common Problems

<details>
<summary>Qt Platform Plugin Error</summary>
If you encounter the following error:

```text
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.

Aborted (core dumped)
```

This issue can be resolved by installing the required Qt library. Run the following command:

```bash
sudo apt-get install libqt5gui5
```
</details>

## Contributing

**Quick start**:

1. Create a branch with new feature from `main` branch (`git checkout -b feat/my-feature develop`)
2. Commit the changes (`git commit -m "feat: Add some awesome feature"`)
3. Push the branch to origin (`git push origin feat/add-amazing-feature`)
4. Open the pull request

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the terms of the **MIT** license. See the [LICENSE](LICENSE.md) for more information.
