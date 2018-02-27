import click

class Output:

    def info(self, text):
        click.secho(text, fg='yellow')

    def status(self, text):
        self.info(text)
        self.line()

    def prompt(self, text):
        click.secho(text, fg='white')

    def error(self, text):
        click.secho("ERROR: " + text, fg='red')

    def header(self, text):
        self.line()
        s = "======== {0} ========".format(text).upper()
        m = "="*len(s)
        click.secho(m, fg='white')
        click.secho(s, fg='white')
        click.secho(m, fg='white')
        self.line()

    def param(self, text, value, status, suppress):
        if value and not suppress:
            self.header("SETTING " + text)
            self.status(status)

    def footer(self, text):
        self.info(text.upper())
        self.line()

    def procout(self, text):
        click.secho(text, dim=True)

    def line(self):
        click.secho("")
