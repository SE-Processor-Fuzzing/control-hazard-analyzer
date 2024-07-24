<h1 align="center"> Summarize</h1>

**Read analysis results and create interactive diagram, saving it as image for easy visualization.**

## Options
- [Help](#help)
- [Source directories](#source-directories)
- [Output directory](#output-directory)
- [Don't show graph](#dont-show-graph)
- [Don't save graph](#dont-save-graph)
- [Log level](#log-level)

### Help
Use the help option to see all available options:
```shell
python3 cha.py summarize --help
```

### Source directories
**Required:** Specify one or more paths to source directories. Directories should contain analysis results in the form of `.data` files.\
By default, the there is no source directory specified, that is why this option is `required`.
#### Usage example:
```shell
# Use specific source directories
python3 cha.py summarize --src-dirs "dir1" "dir2"
```

### Output directory
Specify a custom directory to save the summary results. By default, results will be saved in the `summarize` directory. If the specified directory does not exist, it will be created. And, if the directory is not empty, the existing files will be removed, and overwritten with the new summary results.\
Specified directory will contain summary results in the form of `.data` file and a graph as `graph.png`.
#### Usage example:
```shell
# Save summary results in "outputDir" directory
python3 cha.py summarize --out-dir "outputDir"
```

### Don't show graph
Optionally don't show a graph with summary result. By default, the graph will be shown.
#### Usage example:
```shell
# Do not show the graph
python3 cha.py summarize --no-show-graph
```

### Don't save graph
Optionally don't save a graph with summary result as graph.png. By default, the graph will be saved.
#### Usage example:
```shell
# Do not save the graph
python3 cha.py summarize --no-save-graph
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
python3 cha.py summarize --log-level INFO
```
