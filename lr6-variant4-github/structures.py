"""Двусвязный список, дек на кольцевом массиве и история посещённых страниц."""


class Node:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value, prev=None, next_node=None):
        self.value = value
        self.prev = prev
        self.next = next_node


class DoublyLinkedList:
    __slots__ = ("head", "tail", "_size")

    def __init__(self):
        self.head = self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def push_front(self, value):
        node = Node(value, next_node=self.head)
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self._size += 1

    def push_back(self, value):
        node = Node(value, prev=self.tail)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def pop_front(self):
        if self.head is None:
            raise IndexError("Список пуст")
        old = self.head
        self.head = old.next
        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None
        old.next = None
        self._size -= 1
        return old.value

    def pop_back(self):
        if self.tail is None:
            raise IndexError("Список пуст")
        old = self.tail
        self.tail = old.prev
        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        old.prev = None
        self._size -= 1
        return old.value

    def _node(self, index):
        if not 0 <= index < self._size:
            raise IndexError("Индекс вне списка")
        if index < self._size // 2:
            node = self.head
            for _ in range(index):
                node = node.next
        else:
            node = self.tail
            for _ in range(self._size - 1 - index):
                node = node.prev
        return node

    def get(self, index):
        return self._node(index).value

    def find(self, value):
        return next((i for i, item in enumerate(self) if item == value), -1)

    def insert(self, index, value):
        if index == 0:
            self.push_front(value)
        elif index == self._size:
            self.push_back(value)
        else:
            right = self._node(index)
            node = Node(value, right.prev, right)
            right.prev.next = node
            right.prev = node
            self._size += 1


class ArrayDeque:
    __slots__ = ("_data", "_head", "_size")

    def __init__(self, capacity=8):
        if capacity < 1:
            raise ValueError("Ёмкость должна быть положительной")
        self._data = [None] * capacity
        self._head = self._size = 0

    def __len__(self):
        return self._size

    @property
    def capacity(self):
        return len(self._data)

    def __iter__(self):
        for i in range(self._size):
            yield self._data[(self._head + i) % self.capacity]

    def _ensure_room(self):
        if self._size == self.capacity:
            larger = [None] * (2 * self.capacity)
            for i, value in enumerate(self):
                larger[i] = value
            self._data = larger
            self._head = 0

    def push_front(self, value):
        self._ensure_room()
        self._head = (self._head - 1) % self.capacity
        self._data[self._head] = value
        self._size += 1

    def push_back(self, value):
        self._ensure_room()
        pos = (self._head + self._size) % self.capacity
        self._data[pos] = value
        self._size += 1

    def pop_front(self):
        if not self._size:
            raise IndexError("Дек пуст")
        pos = self._head
        value = self._data[pos]
        self._data[pos] = None
        self._head = (pos + 1) % self.capacity
        self._size -= 1
        return value

    def pop_back(self):
        if not self._size:
            raise IndexError("Дек пуст")
        pos = (self._head + self._size - 1) % self.capacity
        value = self._data[pos]
        self._data[pos] = None
        self._size -= 1
        return value

    def clear(self):
        while self._size:
            self.pop_back()


class BrowserHistory:
    def __init__(self, home):
        self.current = home
        self.past = ArrayDeque()
        self.future = ArrayDeque()

    def visit(self, page):
        self.past.push_back(self.current)
        self.future.clear()
        self.current = page
        return self.current

    def back(self):
        if self.past:
            self.future.push_back(self.current)
            self.current = self.past.pop_back()
        return self.current

    def forward(self):
        if self.future:
            self.past.push_back(self.current)
            self.current = self.future.pop_back()
        return self.current
