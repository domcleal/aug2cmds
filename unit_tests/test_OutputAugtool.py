import aug2cmds
import aug2cmds.outputs
from augeas import Augeas
import os.path
import shutil
import tempfile
import unittest

class FakeNode:
    def setpath(self):
        return "/files/foo[.='bar']"
    def value(self):
        return "bar"
    def children(self):
        return [FakeChild()]

class FakeChild:
    def setpath(self):
        return "/files/foo[.='bar']/test[.='foo']"
    def value(self):
        return "foo"
    def children(self):
        return []

class TestNode(unittest.TestCase):
    """Tests the Augtool output class"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = "%s/root" % self.tmp
        shutil.copytree("%s/fakeroot" % os.path.dirname(__file__), self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_visitnode_fake(self):
        """Test visitnode against two fake nodes"""
        gen = aug2cmds.outputs.Augtool().visitnode(FakeNode())
        self.assertEqual(next(gen), "set /files/foo[.='bar'] 'bar'")
        self.assertEqual(next(gen), "set /files/foo[.='bar']/test[.='foo'] 'foo'")
        self.assertRaises(StopIteration, next, gen)

    def test_visit_fake(self):
        """Test visit against two fake nodes"""
        class FakePathNode:
            def topnode(fself, augpath):
                self.assertEqual(augpath, "/files/foo")
                return FakeNode()
        gen = aug2cmds.outputs.Augtool().visit(FakePathNode(), "/files/foo")
        self.assertEqual(next(gen), "set /files/foo[.='bar'] 'bar'")
        self.assertEqual(next(gen), "set /files/foo[.='bar']/test[.='foo'] 'foo'")
        self.assertRaises(StopIteration, next, gen)

    def test_pathnode_aliases(self):
        """Test with real PathNode against nsswitch.conf aliases"""
        pn = aug2cmds.PathNode("/etc/nsswitch.conf", root=self.root)
        gen = aug2cmds.outputs.Augtool().visit(pn, "database[15]")
        self.assertEqual(next(gen),
          "set /files/etc/nsswitch.conf/database[.='aliases'] 'aliases'")
        self.assertEqual(next(gen),
          "set /files/etc/nsswitch.conf/database[.='aliases']/service[.='files'] 'files'")
        self.assertEqual(next(gen),
          "set /files/etc/nsswitch.conf/database[.='aliases']/service[.='nisplus'] 'nisplus'")
        self.assertRaises(StopIteration, next, gen)

    def test_cmd_clear(self):
        """Check 'clear' is generated when there's no value"""
        class EmptyNode:
            def setpath(self):
                return "/files/foo"
            def value(self):
                return None
            def children(self):
                return []
        gen = aug2cmds.outputs.Augtool().visitnode(EmptyNode())
        self.assertEqual(next(gen), "clear /files/foo")
        self.assertRaises(StopIteration, next, gen)

if __name__ == '__main__':
    unittest.main()
