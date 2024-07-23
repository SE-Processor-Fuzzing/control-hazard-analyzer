<h1 align="center"> Aggregate</h1>

## Options
- [Help](#help)
- [Configuration file](#configuration-file)
- [Section in configuration](#section-in-configuration)
- [Destination directory](#destination-directory)
- [Async analyze](#async-analyze)
- [Log level](#log-level)

### Help
Use the help option to see all available options:
```shell
python3 cha.py aggregate --help
```

### Configuration file
Specify the path to your configuration file. The default is `config.json`.
#### Usage example:
```shell
# Use a specific configuration file
python3 cha.py aggregate --config-file "path/to/config_file"
```

### Section in configuration
Set the custom section in the configuration file. The default section is `DEFAULT`.
#### Usage example:
```shell
# Use a custom section in the configuration file
python3 cha.py aggregate --section-in-config "customSection"
```

### Destination directory
Specify the path to the destination directory. If the directory does not exist, it will be created. The default is `out`.
#### Usage example:
```shell
# Set the destination directory
python3 cha.py aggregate --dest-dir "outputDir"
```

### Async analyze
Run analyze steps simultaneously. This is not recommended with `perf`. By default, this option is off.
#### Usage example:
```shell
# Enable asynchronous analysis
python3 cha.py aggregate --async-analyze
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
python3 cha.py aggregate --log-level INFO
```
