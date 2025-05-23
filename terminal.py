from abc import ABC, abstractmethod
import shlex
from pickle import dump, load


BLUE = '\033[94m'
END = '\033[0m'

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


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
    
    @name.setter
    def name(self, val):
        self._name = val
    
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, val):
        self._parent = val

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
        print('\n'.join(self.content))
    
    def write_line(self, val):
        self.content.append(val)

    def write(self, val):
        if self.content:
            self.content[-1] += val
        else:
            self.content.append(val)

    def delete_line(self, l):
        if l > 0:
            try :
                self.content.pop(l-1)
            except IndexError:
                raise IndexError('line doesn\'t exist')
        else:
            raise IndexError('line must be a positive number')
        
    def edit_line(self, l, value):
        if l > 0:
            try :
                self.content[l-1] = value
            except IndexError:
                raise IndexError('line doesn\'t exist')
        else:
            raise IndexError('line must be a positive number')


@singleton
class FileSystem:
    def __init__(self):
        self.root = DataManager.load_files() or Directory('/', None)
        self.current_dir = self.root
        self.path = []

    def make_directory(self,name, path: str = None):
        target_directory = self._find(path)
        target_directory.children.append(Directory(name, target_directory))

    def _find(self, path: str = None, current_dir = None)-> Directory:
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
                return self._find(new_path,current_dir.parent)
        for child in current_dir.children:
            if child.name == child_name and isinstance(child, FilesystemObject):
                return self._find(new_path, child)
        raise Exception('Directory not found')
        
    def change_directory(self, path: str):
        if path =='..':
            self.current_dir = self.current_dir.parent
            return True
        try:
            directory = self._find(path)
            assert isinstance(directory, Directory)
            self.current_dir = directory
        except :
            raise Exception('Directory not found')
        
    def remove(self, path):
        file = self._find(path)
        file.parent.children.remove(file)

    def make_file(self,name, path = None):
        dir = self._find(path)
        file = TextFile(name, dir)
        dir.children.append(file)

    def move(self, path, new_path):
        obj = self._find(path)
        parent = self._find(new_path)
        obj.parent.children.remove(obj)
        obj.parent = parent
        parent.children.append(obj)

    def copy(self, path, path_to_copy):
        object_to_copy = self._find(path)
        parent_to_copy = self._find(path_to_copy)
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
            directory = self._find(path)
        else:
            directory = self.current_dir
        
        output = map(lambda child: BLUE + child.name + END if isinstance(child, Directory)\
                    else child.name, directory.children)
        print('   '.join(output))
        
    def cat_file(self, path):
        file = self._find(path)
        file.read()

    def append_text(self, path, line):
        file = self._find(path)
        file.write_line(line)

    def delete_line(self, path, l):
        try:
            l = int(l)
            file = self._find(path)
            file.delete_line(l)
        except ValueError:
            raise ValueError('line must be a positive number')
        
    def edit_line(self, path, line, text):
        file = self._find(path)
        try:
            line = int(line)
        except ValueError:
            raise ValueError('line must be a positive number')
        file.edit_line(line, text)

if __name__=="__main__":
    
    f = FileSystem()
    while True:
        try:
            com = shlex.split(input(f'{f.current_dir.path} $ '))
        except:
            print('invalid input')
        try:
            match com[0]:
                case 'mkdir':
                    f.make_directory(*com[1:])
                case 'cd':
                    if len(com) > 1:
                        f.change_directory(com[1])
                    else:
                        f.change_directory('/')
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
                case 'cat':
                    f.cat_file(com[1])
                case 'appendtxt':
                    line = input('>> ')
                    while line != '\\END\\':
                        f.append_text(com[1], line)
                        line = input('>> ')
                case 'editline':
                    text = input('>> ')
                    f.edit_line(*com[1:], text)
                case 'deline':
                    f.delete_line(*com[1:])
                case 'exit':
                    DataManager.save_files(f.root)
                    break
                case _:
                    print('command not found')
        except TypeError as e:
            print('missing name or path')
        except KeyboardInterrupt:
            DataManager.save_files(f.root)
        except Exception as e:
            print(e)