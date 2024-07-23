<h1 align="center"> Generate</h1>

**Configure and create test files based on specified parameters, and store them in a specific directory.**

## Options
- [Help](#help)
- [Output directory](#output-directory)
- [Amount of repeats](#amount-of-repeats)
- [Log level](#log-level)

### Help
Use the help option to see all available options:
```shell
python3 cha.py generate --help
```

### Output directory
Specify a custom directory to save the generated tests. By default, tests will be saved in the tests directory.
#### Usage example:
```shell
# Save generated tests in "myDir" directory
python3 cha.py generate --out-dir "myDir"
```

### Amount of repeats
Set the number of tests to generate. By default, only one test will be generated.
#### Usage example:
```shell
# Generate 10 tests
python3 cha.py generate --repeats 10
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
python3 cha.py generate --log-level INFO
```
