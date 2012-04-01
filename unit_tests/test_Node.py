import aug2cmds
from augeas import Augeas
import os.path
import shutil
import tempfile
import unittest

class TestNode(unittest.TestCase):
    """Tests the Node class"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = "%s/root" % self.tmp
        shutil.copytree("%s/fakeroot" % os.path.dirname(__file__), self.root)

        self.aug = Augeas(root=self.root, flags=Augeas.NO_MODL_AUTOLOAD)
        self.aug.add_transform("Nsswitch.lns", "/etc/nsswitch.conf")
        self.aug.load()

        class FakeParent:
            def setpath(self):
                return "/files/etc/nsswitch.conf"
        self.parent = FakeParent()

    def tearDown(self):
        shutil.rmtree(self.tmp)
        self.aug.close()

    def test_setpath_self(self):
        """Test setpath generates path for '.' (itself)"""
        n = aug2cmds.Node(self.aug, self.parent, uniqpaths=["."],
                          path="/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath(),
                         "/files/etc/nsswitch.conf/database[.='passwd']")

    def test_setpath_subnode(self):
        """Test setpath generates path for a subnode"""
        n = aug2cmds.Node(self.aug, self.parent, uniqpaths=["service"],
                          path="/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath(),
                         "/files/etc/nsswitch.conf/database[service='files']")

    def test_setpath_and(self):
        """Test setpath generates path for multiple subpaths"""
        n = aug2cmds.Node(self.aug, self.parent, uniqpaths=[".", "service"],
                          path="/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath(),
          "/files/etc/nsswitch.conf/database[.='passwd' and service='files']")

    def test_basename(self):
        """Test basename understands Augeas paths"""
        self.assertEqual(aug2cmds.Node.basename("/files"), "files")
        self.assertEqual(aug2cmds.Node.basename("/files/test"), "test")
        self.assertEqual(aug2cmds.Node.basename("/files/test[foo]"), "test")
        self.assertEqual(aug2cmds.Node.basename(
                           "/files/test[foo/bar]"), "test")

    def test_dirname(self):
        """Test dirname understands Augeas paths"""
        self.assertEqual(aug2cmds.Node.dirname("/files"), "/")
        self.assertEqual(aug2cmds.Node.dirname("/files/test"), "/files")
        self.assertEqual(aug2cmds.Node.dirname("/files/test[foo]"), "/files")
        self.assertEqual(aug2cmds.Node.dirname(
                           "/files/test[foo/bar]"), "/files")

    def test_children_none(self):
        """Test when there are no children"""
        n = aug2cmds.Node(self.aug, self.parent,
                          "/files/etc/nsswitch.conf/#comment[1]")
        self.assertRaises(StopIteration, next, n.children())

    def test_children(self):
        """Test new Node objects are created for children"""
        n = aug2cmds.Node(self.aug, self.parent,
                          "/files/etc/nsswitch.conf/database[15]")
        c = n.children()
        sn = c.next()
        self.assertEqual(sn.path,
          "/files/etc/nsswitch.conf/database[15]/service[1]")
        self.assertEqual(sn.setpath(),
          "/files/etc/nsswitch.conf/database[.='aliases']/service[.='files']")

        sn = c.next()
        self.assertEqual(sn.path,
          "/files/etc/nsswitch.conf/database[15]/service[2]")
        self.assertEqual(sn.setpath(),
          "/files/etc/nsswitch.conf/database[.='aliases']/service[.='nisplus']")

        self.assertRaises(StopIteration, next, c)

if __name__ == '__main__':
    unittest.main()
