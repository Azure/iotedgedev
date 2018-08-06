import sys

# We had to implement this custom arg parsing class because Click doesn't have a handler to detect command before any arguments are parsed,
# which we need for the dotenv load command.  We don't want to load dotenv for some commands and we terse output for other commands.


class Args():
    def get_current_command(self):
        if sys.argv and len(sys.argv) > 1 and not self.is_info_command():
            return ' '.join(sys.argv[1:]).strip()
        else:
            return ''

    def is_info_command(self):
        for arg in sys.argv:
            if arg.startswith('--version') or arg.startswith('-h') or arg.startswith('--help'):
                return True
        return False
