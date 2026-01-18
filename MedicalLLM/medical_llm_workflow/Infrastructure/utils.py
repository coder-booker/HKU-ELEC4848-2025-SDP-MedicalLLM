from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Node:
    key: Any
    value: Any
    prev: Optional["Node"] = None
    next: Optional["Node"] = None

class LinkedHashList:
    def __init__(self):
        self._index: dict[Any, Node] = {}
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None

    def get(self, key: Any) -> Node:
        return self._index[key]   # O(1)
    
    def get_prev(self, key: Any) -> Optional[Node]:
        n = self._index[key]
        return n.prev  # O(1)
    
    def get_next(self, key: Any) -> Optional[Node]:
        n = self._index[key]
        return n.next  # O(1)

    # def neighbors(self, key: Any):
    #     n = self._index[key]
    #     return (n.prev.key if n.prev else None, n.next.key if n.next else None)  # O(1)

    def append(self, key: Any, value: Any):
        n = Node(key, value)
        self._index[key] = n
        if self._tail is None:
            self._head = self._tail = n
        else:
            n.prev = self._tail
            self._tail.next = n
            self._tail = n
