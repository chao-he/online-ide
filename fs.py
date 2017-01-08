import os, errno
from stat import S_ISDIR, S_ISREG
import mimetypes, posixpath

if not mimetypes.inited:
    mimetypes.init() # try to read system mime.types

extensions_map = mimetypes.types_map.copy()
extensions_map.update({
    '': 'text/x-c++src',
    '.py': 'python',
    '.c': 'text/x-csrc',
    '.cc': 'text/x-c++src',
    '.tcc': 'text/x-c++src',
    '.cpp': 'text/x-c++src',
    '.cxx': 'text/x-c++src',
    '.h': 'text/x-c++src',
    '.hh': 'text/x-c++src',
    '.java': 'text/x-java',
    '.php': 'text/x-php',
    '.hs': 'text/x-haskell',
    '.md': 'gfm',
    '.html': 'xml'
    })

def guess_type(path):
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def abspath(path):
    path = os.path.expanduser(path)
    if os.path.islink(path):
        path = os.path.realpath(path)
    return os.path.abspath(path)

class FsUtil:
    def __init__(self, root):
        self.root = abspath(root)

    def translate(self, path):
        if not os.path.isabs(path):
            path = abspath(os.path.join(self.root, path))
        if not path.startswith(self.root):
            raise Exception("no such file: " + path)
        return path

    def ls(self, path):
        root = self.translate(path)
        name = os.path.basename(root)
        parent = self.root if root == self.root else self.translate(os.path.join(path, ".."))
        children = []
        for f in os.listdir(root):
            f = os.path.join(root, f)
            s = os.stat(f) 
            path, name, isdir = f, os.path.basename(f), 0 + S_ISDIR(s.st_mode)
            children.append((isdir, name, path, guess_type(path)))
        children = sorted(children, key=lambda x: -x[0])
        return {"path": root, "parent": parent, "children": children}

    def cat(self, path):
        path = self.translate(path)
        parent = os.path.dirname(path)
        try:
            with open(path) as f:
                content = f.read(1024*1024)
        except Exception,e:
            content = e
        return {"path": path, "parent": parent, "content": content, "mode": guess_type(path)}

    def save(self, path, content):
        path = self.translate(path)
        mkdir_p(os.path.dirname(path))
        with open(path, "w") as f:
            f.write(content)
        return "OK"

if __name__ == "__main__":
    fs = FsUtil(".")
    print fs.root
    print fs.ls("../../static")
    # print fs.mkdir("xxx")
    print fs.save("x/y/z/u/v/w/x.cc", "pig")

