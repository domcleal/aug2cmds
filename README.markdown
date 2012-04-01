# aug2cmds: a utility to generate Augeas commands from a file

** This utility's a work in progress, help appreciated **

Augeas has a set of commands and API calls that create and modify nodes in the
tree, but they can be tedious to create.

This utility intends to take an existing file with a particular line or stanza
already in it and generate the set of commands that would create the same set
of nodes in Augeas.

This should be useful primarily in Puppet, but perhaps also as the basis for
other programs using the Augeas API.

## Requirements
Ensure both Augeas and python-augeas bindings are installed and working as
normal.

For development, I suggest you also use:
* nose, for running tests
* pylint, to keep the score over 8 or so

## Issues
Please file any issues or suggestions on Github:
  https://github.com/domcleal/aug2cmds/issues

(Pull requests are preferred at this stage!)
