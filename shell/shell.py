#!/usr/bin/env python3

# Author: Stephanie Galvan
# Class: Theory of Operating Systems
# Assignment 1: Shell
# Python version: 3.7.0
# Description: To build a user shell for a Unix operating system

import os
import re
import sys
from aifc import Error


class NoArgumentsError(Error):
    """Raised when no argument was provided"""
    pass


class TooManyArgumentsError(Error):
    """Raised when there are too many arguments"""
    pass


while True:
    # default prompt
    command_string = '$ '
    if 'PS1' in os.environ:
        command = os.environ['PS1']

    command = input(command_string)
    args = command.split()

    # when empty, do nothing and continue
    if not args:
        continue

    # exit command
    elif args[0] == "exit":
        sys.exit(0)

    # change directories
    elif args[0] == "cd":
        try:
            if len(args) < 2:
                raise NoArgumentsError
            elif len(args) > 2:
                raise TooManyArgumentsError
            else:
                os.chdir(args[1])
        except NoArgumentsError:
            os.write(2, "Error: Provide a directory".encode())
        except TooManyArgumentsError:
            os.write(2, "Error: Too many arguments".encode())
        except FileNotFoundError:
            os.write(2, ("Error: Directory %s not found\n" % args[1]).encode())

    # fork, exec, wait
    else:
        rc = os.fork()

        # fork failure
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        # child
        elif rc == 0:

            if ">" in args or "<" in args:
                i = -1
                if ">" in args:
                    i = args.index('>')
                else:
                    i = args.index('<')

                os.close(1)
                os.open(args[i + 1], os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1, True)
                args = args[0:i]

            for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # try to exec program
                except FileNotFoundError:  # ...expected
                    pass  # ...fail quietly

            os.write(2, ("command not found %s\n" % (args[0])).encode())
            sys.exit(1)  # terminate with error

        # parent (forked ok)
        else:
            # process done
            os.wait()
