# Control hazard analyzer

**Control hazard analyzer** *(abbreviated `cha.py`)* is toolchain for analyzing control hazards.

---

## Requirements
- Python 3.8+

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

### generate
**Usage example:**
```bash
python3 cha.py generate --repeats=100 --dest_folder="out"
```

### analyze
**Usage example:**
```bash
python3 cha.py analyze --test_dir="out/src" --profiler="perf"
```

### summarize
**Usage example:**
```bash
python3 cha.py summarize
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
