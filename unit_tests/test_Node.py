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

    def tearDown(self):
        shutil.rmtree(self.tmp)
        self.aug.close()

    def test_setpath_self(self):
        """Test setpath generates path for '.' (itself)"""
        n = aug2cmds.Node(self.aug, "/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath(["."]),
                         "/files/etc/nsswitch.conf/database[.='passwd']")

    def test_setpath_subnode(self):
        """Test setpath generates path for a subnode"""
        n = aug2cmds.Node(self.aug, "/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath(["service"]),
                         "/files/etc/nsswitch.conf/database[service='files']")

    def test_setpath_and(self):
        """Test setpath generates path for multiple subpaths"""
        n = aug2cmds.Node(self.aug, "/files/etc/nsswitch.conf/database[1]")
        self.assertEqual(n.setpath([".", "service"]),
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

if __name__ == '__main__':
    unittest.main()
