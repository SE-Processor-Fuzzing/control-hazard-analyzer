# Control hazard analyzer

<p align="center">
<a href="https://github.com/osogi/control-hazard-analyzer/actions"><img alt="Actions Status" src="https://github.com/osogi/control-hazard-analyzer/actions/workflows/github-actions.yml/badge.svg"></a>
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
- gem5

## Installation

```bash
python3 -m pip install -r requirements.txt
```

For using gemProofiler you need to have gem5 and library M5ops:
- [gem5 installation](https://www.gem5.org/getting_started/)
- [M5ops installation](https://www.gem5.org/documentation/general_docs/m5ops/)

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

```bash
python3 cha.py aggregate --help
```

### generate

**Usage example:**

```bash
python3 cha.py generate --repeats=10 --out_dir="out" --debug
```

### analyze

**Usage example:**

```bash
python3 cha.py analyze --test_dir="out" --out_dir="perf_result" --debug
```

### summarize

**Usage example:**

```bash
python3 cha.py summarize --src-dirs="perf_result" --out_dir="summarize_result" --debug
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

## Contributing

**Quick start**:

1. Create a branch with new feature from `main` branch (`git checkout -b feat/my-feature develop`)
2. Commit the changes (`git commit -m "feat: Add some awesome feature"`)
3. Push the branch to origin (`git push origin feat/add-amazing-feature`)
4. Open the pull request

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the terms of the **MIT** license. See the [LICENSE](LICENSE.md) for more information.
