from abc import ABC, abstractmethod



class FilesystemObject(ABC):
    def __init__(self, name, parent):
        self._name = name
        self._parent = parent

    @property
    def name(self):
        return self._name
    
    @property
    def parent(self):
        return self._parent


class Directory(FilesystemObject):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._children = []
    
    @property
    def children(self):
        return self._children
    
    @property
    def path(self):
        path = ''
        dir = self
        while dir.parent:
            path = '/' + dir.name + path
            dir = dir.parent
        return path
    

class TextFile(FilesystemObject):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.content = []

    def read(self):
        return '\n'.join(self.content)
    
    def write_line(self, val):
        self.content.append(val)

    def write(self, val):
        self.content[-1] += val


class FileSystem:
    def __init__(self):
        self.root = Directory('/', None)
        self.current_dir = self.root
        self.path = []

    def make_directory(self,name, path: str = None):
        target_directory = self.find_dir(path)
        target_directory.children.append(Directory(name, target_directory))

    def find_dir(self, path: str = None, current_dir = None)-> Directory:
        if not current_dir:
            current_dir = self.current_dir
        if not path:
            return current_dir
        if path == '/':
            return self.root
        elif path.startswith('/'):
            current_dir = self.root
        child_name = path.strip('/').split('/')[0]
        for child in current_dir.children:
            if child.name == child_name and isinstance(child, Directory):
                new_path = '/'.join(path.strip('/').split('/')[1:])
                return self.find_dir(new_path, child)
        raise Exception('Directory not found')
        
    def change_directory(self, path: str):
        try:
            Directory = self.find_dir(path)
            self.current_dir = Directory
            return True
        except :
            raise Exception('Directory not found')
        
    def remove(self, path):
        file = self.find_dir(path)
        file.parent.children.remove(file)

    def make_file(self, path, name):
        dir = self.find_dir(path)
        file = TextFile(name, dir)
        dir.children.append(file)
        

        
f = FileSystem()
f.make_directory(name= 'downloads')
f.make_directory(name= 'pictures')
f.change_directory('/pictures')
print(f.current_dir.name)
f.make_directory('camera')
f.change_directory('/')
print(f.current_dir.name)
f.make_directory(name = 'documents')
f.change_directory('/pictures/camera')
print(f.current_dir.name)
f.make_directory('screenshots', '/pictures')
f.make_file(f.current_dir.path, 'file1.txt')

l1 = [d.name for d in f.root.children]
l2 = [d.name for d in f.current_dir.children]
print(l1)
print(l2)
