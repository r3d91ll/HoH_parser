import os
import tempfile
from hoh_parser.utils.file_ops import list_py_files

def test_list_py_files_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some .py and non-.py files
        py1 = os.path.join(tmpdir, "a.py")
        py2 = os.path.join(tmpdir, "b.py")
        nonpy = os.path.join(tmpdir, "c.txt")
        with open(py1, "w") as f:
            f.write("# test python file 1")
        with open(py2, "w") as f:
            f.write("# test python file 2")
        with open(nonpy, "w") as f:
            f.write("not python")
        files = list_py_files(tmpdir)
        assert py1 in files
        assert py2 in files
        assert nonpy not in files

def test_list_py_files_recursive():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "subdir1"))
        os.makedirs(os.path.join(tmpdir, "subdir2"))
        py1 = os.path.join(tmpdir, "subdir1", "x.py")
        py2 = os.path.join(tmpdir, "subdir2", "y.py")
        with open(py1, "w") as f:
            f.write("# subdir python file 1")
        with open(py2, "w") as f:
            f.write("# subdir python file 2")
        files = list_py_files(tmpdir)
        assert py1 in files
        assert py2 in files
        assert all(f.endswith('.py') for f in files)
