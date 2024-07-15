# Making edits

## Basic Tips

1. Don't use merge, only rebase (to keep a linear commit history)
2. Do not change other people's branches unless absolutely necessary
3. Recheck your commit history before creating a pull request
4. **Check you're on the right branch**, never commit directly in main

## Rules for adding commits

Create a new branch, if you want to add something new. Naming branch is `<type>/<name of stuff>`. \
Commits are added according to conventional commits. Those
`<type>(<scope>): <body>`.

The `<type>` field must take one of these values:

* `feat` to add new functionality
* `fix` to fix a bug in the program
* `refactor` for code refactoring, such as renaming a variable
* `test` to add tests, refactor them
* `struct` for changes related to a change in the structure of the project (BUT NOT CODE), for example, changing
  folder locations
* `ci` for various ci/cd tasks
* `docs` for changes in documentation

The `<body>` field contains the gist of the changes in the present imperative in English without the dot in
at the end, the first word is a verb with a small letter.
Examples:

* Good: "feat: add module for future BST implementations"
* Bad: "Added module for future BST implementations."

## Rules for pull requests

**Forbidden** to merge your pull request into the branch yourself.

If you click on the green button, then **make sure** that it says `REBASE AND MERGE`

The review takes place in the form of comments to pull requests, discussions in the team chat and personal
communication.
