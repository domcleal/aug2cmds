"""Generators to create different output formats."""

class Augtool:
    """Visits each node in turn and generates augtool set commands"""
    def visit(self, pathnode, augpath):
        """Generates augtool set commands for everything below augpath in
        pathnode"""
        topnode = pathnode.topnode(augpath)
        return self.visitnode(topnode)

    def visitnode(self, node):
        """Generates augtool set commands for everything below node"""
        setpath = node.setpath()
        value = node.value()
        if value:
            # FIXME: quoting
            command = "set %s '%s'" % (setpath, value)
        else:
            command = "clear %s" % setpath
        yield command

        # Recurse depth-first and yield all commands
        for child in node.children():
            for childcmd in self.visitnode(child):
                yield childcmd

