#!/usr/bin/env python

"""aug2cmds converts an Augeas tree into a set of Augeas commands

Designed for use with augtool and Puppet."""

from augeas import Augeas
import os

class Node:
    """Represents a node in the tree that we will be creating commands for."""
    aug = None

    def __init__(self, aug, path):
        self.aug = aug
        self.path = path

    @classmethod
    def basename(cls, path):
        """Returns the node label given a path."""
        return cls.__basehelper(path, True)

    @classmethod
    def dirname(cls, path):
        """Returns the path up until the last node given a path."""
        return cls.__basehelper(path, False)

    @classmethod
    def __basehelper(cls, path, base):
        """Understands that slashes can be contained in brackets""" 
        sbracket = 0
        # Count backwards to find last slash outside brackets
        for c in range(len(path))[::-1]:
            if path[c] == ']':
                sbracket -= 1
            elif path[c] == '[':
                sbracket += 1
            elif path[c] == '/' and sbracket == 0:
                if base:
                    # strip off path expressions
                    end = path.find("[", c+1)
                    if end > 0:
                        return path[c+1:end]
                    else:
                        return path[c+1:]
                else:
                    if c == 0:
                        # special case: root
                        return path[0]
                    else:
                        return path[:c]

    def setpath(self, uniqpaths):
        """Generate a path for use in `set` commands to represent this node.

        Path is based on a unique value that will be contained inside an XPath
        type expression.

        :param uniqpaths: list of paths relative to this node that make it
        unique, e.g. ["."], ["ipaddr", "canonical"]"""

        # FIXME: quoting
        # FIXME: how to handle seqs?
        return "%s/%s[%s]" % (self.dirname(self.path),
                              self.basename(self.path),
                              " and ".join(
                                ["%s='%s'" % (subpath, self.aug.get("%s/%s" %
                                                (self.path, subpath)))
                                 for subpath in uniqpaths]))

class PathNode(Node):
    """Top level Augeas node representing the file itself."""

    def __init__(self, path, root=None, lens=None):
        """Opens Augeas and checks `path` loaded.

        :param path: file path to load
        :param root: use as root directory of filesystem
        :param lens: load `path` specifically with this Augeas lens"""

        if lens and path[0] != "/":
            # Convert relative path to abs if lens given
            path = ("%s/%s" % (os.getcwd(), path)).replace("//", "")
        elif not root and path[0] != "/":
            # Assume root is here if relative path given
            root = os.getcwd()
            path = "/%s" % path

        flags = Augeas.NONE
        if lens:
            flags = Augeas.NO_MODL_AUTOLOAD

        aug = Augeas(root=root, flags=flags)
        Node.__init__(self, aug, "/files%s" % path)

        if lens:
            self.aug.add_transform(lens, path)
            self.aug.load()

        # Check the file parsed
        if not self.aug.match(self.path):
            raise RuntimeError("Parsing of %s failed" % path)

    def __del__(self):
        """Cleanly close Augeas."""
        if self.aug:
            self.aug.close()

    def topnode(self, augpath=None):
        """Gets the top `Node` from augpath relative to this file."""

        if not augpath:
            return self

        # Expect one node to be matched beneath the file
        toppath = self.aug.match("%s/%s" % (self.path, augpath))
        if not toppath:
            raise RuntimeError("Unable to match %s in %s" % \
                                   (augpath, self.path))

        if len(toppath) > 1:
            raise RuntimeError("Too many matches for %s in %s" % \
                                   (augpath, self.path))

        toppath = toppath.pop()
        if toppath == self.path:
            return self

        return Node(self.aug, toppath)
