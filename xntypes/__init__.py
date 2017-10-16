__all__ = ["File", "ListStack", "NodeStack", "ListNode", "ArrayStack"]


class File:
    VERSION = "0.0.1"
    __slots__ = ["name", "folder", "extension"]

    def __init__(self, name, folder, extension):
        self.name = name
        self.folder = folder
        self.extension = extension

    def reload_exts(self):
        ext_list = self.name.split(".")
        self.extension = ext_list[-1]


class ListNode:
    def __init__(self, item=None, link=None):
        self.__item = item
        self.__link = link

    def get_item(self):
        return self.__item

    def set_item(self, item):
        self.__item = item

    def get_link(self):
        return self.__link

    def set_link(self, link):
        self.__link = link


class NodeStack:
    def __init__(self, max=int(1e27)):
        self.__top = None
        self.__size = 0
        self.max = max

    def __len__(self):
        return self.__size

    def destroy(self):
        self.__top = None

    def is_empty(self):
        return self.__top is None

    def is_full(self):
        return self.__size == self.max

    def push(self, item):
        if self.is_full():
            raise IndexError('Stack is full')
        self.__top = ListNode(item, self.__top)
        self.__size += 1

    def pop(self):
        if self.is_empty():
            raise IndexError('Empty stack')
        item = self.__top.get_item()
        self.__top = self.__top.get_link()
        self.__size -= 1
        return item

    def top(self):
        if self.is_empty():
            raise IndexError('Empty stack')
        return self.__top.get_item()


class ListStack(list):
    def push(self, item):
        self.append(item)

    def is_empty(self):
        return not self

    def top(self):
        return self[-1]

    def pop(self):
        return super().pop(-1)


class ArrayStack:
    def __init__(self):
        self.__data = []

    def __len__(self):
        return len(self.__data)

    def is_empty(self):
        return len(self.__data) == 0

    def push(self,e):
        self.__data.append(e)

    def top(self):
        if self.is_empty():
            raise Exception('Stack is empty')
        return self.__data[-1]

    def pop(self):
        if self.is_empty():
            raise Exception('Stack is empty')
        return self.__data.pop()
