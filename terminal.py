from abc import ABC, abstractmethod
import shlex
from pickle import dump, load


BLUE = '\033[94m'
END = '\033[0m'

class DataManager:

    @staticmethod
    def load_files():
        try :
            with open('files.pkl', 'rb') as f:
                root = load(f)
                return root
        except FileNotFoundError:
            return None

    @staticmethod
    def save_files(root):
        with open('files.pkl', 'wb') as f:
            dump(root, f)


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
        self.root = DataManager.load_files() or Directory('/', None)
        self.current_dir = self.root
        self.path = []

    def make_directory(self,name, path: str = None):
        target_directory = self.find(path)
        target_directory.children.append(Directory(name, target_directory))

    def find(self, path: str = None, current_dir = None)-> Directory:
        if not current_dir:
            current_dir = self.current_dir
        if not path:
            return current_dir
        if path == '/':
            return self.root
        elif path.startswith('/'):
            current_dir = self.root
        child_name = path.strip('/').split('/')[0]
        new_path = '/'.join(path.strip('/').split('/')[1:])
        if child_name == '..':
                return self.find(new_path,current_dir.parent)
        for child in current_dir.children:
            if child.name == child_name and isinstance(child, FilesystemObject):
                return self.find(new_path, child)
        raise Exception('Directory not found')
        
    def change_directory(self, path: str):
        if path =='..':
            self.current_dir = self.current_dir.parent
            return True
        try:
            directory = self.find(path)
            assert isinstance(directory, Directory)
            self.current_dir = directory
        except :
            raise Exception('Directory not found')
        
    def remove(self, path):
        file = self.find(path)
        file.parent.children.remove(file)

    def make_file(self,name, path = None):
        dir = self.find(path)
        file = TextFile(name, dir)
        dir.children.append(file)

    def move(self, path, new_path):
        obj = self.find(path)
        parent = self.find(new_path)
        obj.parent.children.remove(obj)
        obj.parent = parent
        parent.children.append(obj)

    def copy(self, path, path_to_copy):
        object_to_copy = self.find(path)
        parent_to_copy = self.find(path_to_copy)
        if isinstance(object_to_copy, Directory):
            new_dir = Directory(object_to_copy.name, parent_to_copy)
            parent_to_copy.children.append(new_dir)
            for child in object_to_copy.children:
                self.copy(object_to_copy.path + '/' + child.name, new_dir.path)
        elif isinstance(object_to_copy, TextFile):
            new_file = TextFile(object_to_copy.name, parent_to_copy)
            new_file.content = object_to_copy.content.copy()
            parent_to_copy.children.append(new_file)

    def where_am_i(self):
        print(self.current_dir.path or 'root')

    def show_directory(self, path=None):
        if path:
            directory = self.find(path)
        else:
            directory = self.current_dir
        
        output = map(lambda child: BLUE + child.name + END if isinstance(child, Directory)\
                    else child.name, directory.children)
        print('   '.join(output))


if __name__=="__main__":
    
    f = FileSystem()
    while True:
        try:
            com = shlex.split(input('$ '))
        except:
            print('invalid input')
        try:
            match com[0]:
                case 'mkdir':
                    f.make_directory(*com[1:])
                case 'cd':
                    f.change_directory(com[1])
                case 'touch':
                    f.make_file(*com[1:])
                case 'rm':
                    f.remove(com[1])
                case 'ls':
                    f.show_directory(*com[1:])
                case 'mv':
                    f.move(*com[1:])
                case 'cp':
                    f.copy(*com[1:])
                case 'pwd':
                    f.where_am_i()
                case 'exit':
                    DataManager.save_files(f.root)
                    break
                case _:
                    print('command not found')
        except Exception as e:
            print(e)