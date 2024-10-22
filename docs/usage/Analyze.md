<h1 align="center"> Analyze</h1>

**Execute test analyses, generate results, and save them in specific directory.**

## Options
- [Help](#help)
- [Config file](#config-file)
- [Output directory](#output-directory)
- [Tests directory](#tests-directory)
- [Timeout](#timeout)
- [Path to Compiler](#path-to-compiler)
- [Compiler Arguments](#compiler-arguments)
- [Profiler](#profiler)
- [Path to gem5 Home](#path-to-gem5-home)
- [Path to gem5 Binary](#path-to-gem5-binary)
- [Target ISA](#target-isa)
- [Path to simulation script](#path-to-simulation-script)
- [Log level](#log-level)

### Help
Use the help option to see all available options:
```shell
python3 cha.py analyze --help
```

### Config file
Specify the path to the configuration file. By default, there is no configuration file specified.\
**Note**: Configuration file is a `JSON` file that contains all the necessary parameters for the analysis.
#### Usage example:
```shell
# Use a specific configuration file
python3 cha.py analyze --config-file "path/to/config_file"
```

### Output directory
Specify a custom directory to save the analysis results. By default, results will be saved in the `chapy-analyze` directory. Specified directory will contain analysis results in the form of `.data` file.\
**Note**: If the specified directory does not exist, it will be created. And, if the directory is not empty, the existing files will be removed, and overwritten with the new analysis results.
#### Usage example:
```shell
# Save analysis results in "outputDir" directory
python3 cha.py analyze --out-dir "outputDir"
```

### Tests directory
Specify the path to the directory containing the tests. By default, tests are expected in the `chapy-tests` directory. Directory should contain one or more test files written in `C language`.
#### Usage example:
```shell
# Use tests from "testsDir" directory
python3 cha.py analyze --test-dir "testsDir"
```
### Timeout
Set the number of seconds after which the test will be stopped. The default is `10` seconds.
#### Usage example:
```shell
# Set timeout to 30 seconds
python3 cha.py analyze --timeout 30
```
### Path to Compiler
Specify the path to the compiler. The default compiler is `gcc`.
#### Usage example:
```shell
# Use a custom compiler
python3 cha.py analyze --compiler "path/to/compiler"
```

### Compiler Arguments
Pass additional arguments to the compiler. By default, no arguments are passed.
#### Usage example:
```shell
# Pass arguments to the compiler
python3 cha.py analyze --compiler-args "-O2 -Wall"
```
### Profiler
Specify the type of profiler to use. The default is `perf`.
#### Usage example:
```shell
# Use a different profiler
python3 cha.py analyze --profiler otherProfiler
```

### Path to gem5 Home
Specify the path to the gem5 home directory. By default, the gem5 home directory is `./thirdparty/gem5/`.
#### Usage example:
```shell
# Set gem5 home directory
python3 cha.py analyze --gem5-home "path/to/gem5_home"
```
### Path to gem5 Binary
Specify the path to the gem5 binary. By default, the gem5 binary path is `./`.
#### Usage example:
```shell
# Set gem5 binary path
python3 cha.py analyze --gem5-bin "path/to/gem5_bin"
```
### Target ISA
Specify the type of architecture being simulated. By default, the target ISA is not specified.
#### Usage example:
```shell
# Set target ISA
python3 cha.py analyze --target-isa "x86"
```
### Path to simulation script
Specify the path to the simulation script. By default, the simulation script path is root directory `./`.
#### Usage example:
```shell
# Set simulation script path
python3 cha.py analyze --sim-script "path/to/sim_script"
```

### Log level
Control the verbosity of log messages by setting the log level. The default level is `WARNING`. Choose from the following options:
- `DEBUG`: Shows detailed information, typically useful for diagnosing problems. Use this level for development and debugging purposes
- `INFO`: Provides confirmation that things are working as expected. This level is generally used to inform users about the progress and state of the application
- `WARNING`: Indicates that something unexpected happened, or a potential problem is detected, but the application is still running as expected. This level helps to highlight issues that might need attention in the future
- `ERROR`: Signifies that a serious problem has occurred, and the application has not been able to perform some function. This level is used to indicate errors that prevent the program from continuing some operation
- `CRITICAL`: Represents a very serious error, indicating that the program itself may be unable to continue running. This level is used for critical issues that require immediate attention

#### Usage example:
Pass the desired log level using the --log-level option. For example, to set the log level to `INFO`:
```shell
python3 cha.py analyze --log-level INFO
```
