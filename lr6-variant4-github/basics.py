"""Общая часть методики: односвязный список, стек и очередь на кольцевом буфере."""

from structures import ArrayDeque


class SingleNode:
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class SinglyLinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0

    def __len__(self):
        return self.size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def _node(self, index):
        if not 0 <= index < self.size:
            raise IndexError("Индекс вне списка")
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def push_front(self, value):
        self.head = SingleNode(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self.size += 1

    def push_back(self, value):
        node = SingleNode(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def pop_front(self):
        if self.head is None:
            raise IndexError("Список пуст")
        value = self.head.value
        self.head = self.head.next
        self.size -= 1
        if self.head is None:
            self.tail = None
        return value

    def get(self, index):
        return self._node(index).value

    def find(self, value):
        return next((i for i, item in enumerate(self) if value == item), -1)

    def insert(self, index, value):
        if index == 0:
            self.push_front(value)
        elif index == self.size:
            self.push_back(value)
        else:
            if not 0 < index < self.size:
                raise IndexError("Индекс вне списка")
            prev = self._node(index - 1)
            prev.next = SingleNode(value, prev.next)
            self.size += 1


class Stack:
    def __init__(self):
        self.data = []

    def push(self, value):
        self.data.append(value)

    def pop(self):
        return self.data.pop()

    def top(self):
        return self.data[-1]


class RingQueue:
    def __init__(self):
        self.buffer = ArrayDeque()

    def enqueue(self, value):
        self.buffer.push_back(value)

    def dequeue(self):
        return self.buffer.pop_front()
