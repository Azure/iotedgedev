import click


class OrganizedGroup(click.Group):
    """A subclass of click.Group which allows specifying an `order` parameter (0 by default) to sort the commands and groups"""

    def __init__(self, *args, **kwargs):
        self.orders = {}
        super(OrganizedGroup, self).__init__(*args, **kwargs)

    def get_help(self, ctx):
        self.list_commands = self.list_commands_for_help
        return super(OrganizedGroup, self).get_help(ctx)

    def list_commands_for_help(self, ctx):
        """reorder the list of commands when listing the help"""
        commands = super(OrganizedGroup, self).list_commands(ctx)
        return (c[1] for c in sorted(
            (self.orders.get(command, 0), command)
            for command in commands))

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except capture
        a priority for listing command names in help.
        """
        order = kwargs.pop('order', 0)
        orders = self.orders

        def decorator(f):
            cmd = super(OrganizedGroup, self).command(*args, **kwargs)(f)
            orders[cmd.name] = order
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        """Behaves the same as `click.Group.group()` except capture
        a priority for listing command names in help.
        """
        order = kwargs.pop('order', 0)
        orders = self.orders

        def decorator(f):
            cmd = super(OrganizedGroup, self).group(*args, **kwargs)(f)
            orders[cmd.name] = order
            return cmd

        return decorator
