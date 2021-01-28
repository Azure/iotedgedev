import click


class Output:

    def info(self, text, suppress=False):
        if not suppress:
            self.echo(text, color='yellow')

    def warning(self, text):
        self.echo("Warning: %s" % text, color='yellow')

    def status(self, text):
        self.info(text)
        self.line()

    def prompt(self, text):
        self.echo(text, color='white')

    def error(self, text):
        self.echo("ERROR: " + text, color='red', err=True)

    def header(self, text, suppress=False):

        if not suppress:
            self.line()
            s = "======== {0} ========".format(text).upper()
            m = "="*len(s)
            self.echo(m, color='white')
            self.echo(s, color='white')
            self.echo(m, color='white')
            self.line()

    def param(self, text, value, status, suppress):
        if value and not suppress:
            self.header("SETTING " + text)
            self.status(status)

    def footer(self, text, suppress=False):
        if not suppress:
            self.info(text.upper())
            self.line()

    def procout(self, text, nl=True):
        self.echo(text, dim=True, nl=nl)

    def line(self):
        self.echo(text="")

    def echo(self, text, color="", dim=False, nl=True, err=False):
        try:
            click.secho(text, fg=color, dim=dim, nl=nl, err=err)
        except Exception:
            print(text)

    def confirm(self, text, default=False, abort=True):
        return click.confirm(text, default=default, abort=abort)
