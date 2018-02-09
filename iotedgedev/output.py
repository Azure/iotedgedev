import click

class Output:

    def info(self, text):
        click.secho(text, fg='yellow')

    def prompt(self, text):
        click.secho(text, fg='white')

    def error(self, text):
        click.secho("ERROR: " + text, fg='red')

    def header(self, text):
        self.line()
        click.secho("======== {0} ========".format(text).upper(), fg='white')

    def footer(self, text):
        self.info(text.upper())
        self.line()

    def procout(self, text):
        click.secho(text, dim=True)

    def line(self):
        click.secho("")
