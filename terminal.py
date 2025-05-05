

class directory:
    def __init__(self, name, parent):
        self.name = name
        self.files = []
        self._parent = parent
        self._children = []

    @property
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        return self._children
    
    @property
    def path(self):
        path = ''
        dir = self
        while dir.parent:
            path = '/' + dir.name + path
        return path
    
    

class TextFile:
    pass


class FileSystem:
    def __init__(self):
        self.root = directory('/', None)
        self.current_dir = self.root
        self.path = []

    def make_directory(self,name, path: str = None):
        target_directory = self.find_dir(path)
        target_directory.children.append(directory(name, target_directory))

    def find_dir(self, path: str = None, current_dir = None)-> directory:
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
            if child.name == child_name:
                new_path = '/'.join(path.strip('/').split('/')[1:])
                return self.find_dir(new_path, child)
        raise Exception('directory not found')
        
    def change_directory(self, path: str):
        try:
            directory = self.find_dir(path)
            self.current_dir = directory
            return True
        except :
            raise Exception('directory not found')
        

        
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
f.change_directory('/')
f.change_directory('pictures/screenshots/fksjvdf')

l1 = [d.name for d in f.root.children]
l2 = [d.name for d in f.current_dir.children]
print(l1)
print(l2)
