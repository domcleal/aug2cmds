import aug2cmds
import os.path
import shutil
import tempfile
import unittest

class TestPathNode(unittest.TestCase):
    """Tests the PathNode class"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = "%s/root" % self.tmp
        shutil.copytree("%s/fakeroot" % os.path.dirname(__file__), self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_noroot(self):
        """Test constructor without root, requires /etc/hosts"""
        self.assertTrue(aug2cmds.PathNode("/etc/hosts"))

    def test_root(self):
        """Test constructor with fake root"""
        self.assertTrue(aug2cmds.PathNode("/etc/hosts", root=self.root))

    def test_relpath(self):
        """Test supplying relative path, cwd is taken as root"""
        oldcwd = os.getcwd()
        try:
            os.chdir(self.root)
            self.assertTrue(aug2cmds.PathNode("etc/hosts"))
        finally:
            os.chdir(oldcwd)

    def test_lens(self):
        """Test supplying lens as optimisation"""
        shutil.move("%s/etc/hosts" % self.root, "%s/etc/test" % self.root)
        n = aug2cmds.PathNode("/etc/test", lens="Hosts.lns", root=self.root)
        self.assertTrue(n)
        self.assertEqual(len(n.aug.match("/augeas/load//incl")), 1)

    def test_lens_relpath(self):
        """Test supplying lens and relative path"""
        shutil.move("%s/etc/hosts" % self.root, "%s/etc/test" % self.root)
        oldcwd = os.getcwd()
        try:
            os.chdir(self.root)
            n = aug2cmds.PathNode("etc/test", lens="Hosts.lns")
            self.assertTrue(n)
            self.assertEqual(len(n.aug.match("/augeas/load//incl")), 1)
        finally:
            os.chdir(oldcwd)

    def test_parsefail(self):
        """Test exception thrown for failed parse"""
        self.assertRaises(RuntimeError,
                          aug2cmds.PathNode, "/etc/foo", root=self.root)

    def test_destructor(self):
        """Test destructor closes Augeas"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)

        class FakeAugeas:
            closed = False
            def close(self):
                self.closed = True

        # Swap real PathNode.aug for fake class
        n.aug.close()
        aug = FakeAugeas()
        n.aug = aug

        # Check destructor closes Augeas
        del n
        self.assertTrue(aug.closed)

    def test_topnode_nopath(self):
        """Check topnode returns itself if no augpath needed"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)
        self.assertTrue(n.topnode() is n)

    def test_topnode_nomatch(self):
        """Check it raises error if augpath doesn't match"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)
        self.assertRaises(RuntimeError, n.topnode, "foo")

    def test_topnode_manymatches(self):
        """Check it raises error if augpath matches too much"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)
        self.assertRaises(RuntimeError, n.topnode, "*")

    def test_topnode_itself(self):
        """Check topnode returns itself if augpath matches node"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)
        self.assertTrue(n.topnode("../hosts") is n)

    def test_topnode_newnode(self):
        """Check topnode returns a new node when augpath matches"""
        n = aug2cmds.PathNode("/etc/hosts", root=self.root)
        self.assertTrue(n)
        tn = n.topnode("1")
        self.assertTrue(isinstance(tn, aug2cmds.Node))
        self.assertFalse(isinstance(tn, aug2cmds.PathNode))

if __name__ == '__main__':
    unittest.main()
