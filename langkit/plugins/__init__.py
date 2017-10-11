from langkit.passes import AbstractPass
from langkit.utils import Colors, printcol


class PluginMetaclass(type):
    """This Python metaclass keeps track of any Plugin classes created anywhere
    in the code base, be it in langkit itself, or in User-provided plugin
    code. Langkit will automatically invoke any plugins defined by extending
    the Plugin class."""

    plugins = []

    def __new__(cls, *args, **kwargs):
        new_class = super(PluginMetaclass, cls).__new__(cls, *args, **kwargs)
        PluginMetaclass.plugins.append(new_class)
        return new_class

    @staticmethod
    def get_plugins():
        return PluginMetaclass.plugins[1:]


class Plugin(AbstractPass):
    """Langkit and User-written plugins should extend this class and implement
    the 'run' method. Langkit will automatically invoke any plugins extending
    this class."""

    __metaclass__ = PluginMetaclass

    def run(self, context):
        if context.verbosity.info:
            printcol('{}...'.format(self.name), Colors.OKBLUE)
