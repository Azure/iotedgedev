import sys

# We had to implement this custom arg parsing class because Click doesn't have a handler to detect command before any arguments are parsed, which we need for the dotenv load command.  We don't want to load dotenv for some commands and we terse output for other commands.


class Args():
    def get_current_command(self):
        if sys.argv and len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return ''
