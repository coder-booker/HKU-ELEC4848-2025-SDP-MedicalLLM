"""基础数据结构工具模块。

当前提供一个“哈希索引 + 双向链表”的轻量容器，
用于在保持插入顺序的同时支持 O(1) 邻居/节点查询。
"""
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Node:
    """双向链表节点，保存键值及前后指针。"""
    key: Any
    value: Any
    prev: Optional["Node"] = None
    next: Optional["Node"] = None

class LinkedHashList:
    """带哈希索引的双向链表。"""

    def __init__(self):
        # `_index` 用于 O(1) 定位节点，链表负责保持顺序。
        self._index: dict[Any, Node] = {}
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None

    def get(self, key: Any) -> Optional[Node]:
        """按 key 获取节点。"""
        return self._index.get(key)   # O(1)
    
    def get_prev(self, key: Any) -> Optional[Node]:
        """获取指定 key 对应节点的前驱节点。"""
        n = self.get(key)
        return n.prev if n is not None else None  # O(1)
    
    def get_next(self, key: Any) -> Optional[Node]:
        """获取指定 key 对应节点的后继节点。"""
        n = self.get(key)
        return n.next if n is not None else None  # O(1)
    
    def get_tail(self) -> Optional[Node]:
        """获取链表尾节点。"""
        return self._tail

    def get_all(self) -> list[Any]:
        """按插入顺序返回所有节点 value。"""
        values = []
        current = self._head
        # 从头到尾遍历链表，保持时序输出。
        while current is not None:
            values.append(current.value)
            current = current.next
        return values

    # def neighbors(self, key: Any):
    #     n = self._index[key]
    #     return (n.prev.key if n.prev else None, n.next.key if n.next else None)  # O(1)

    def append(self, key: Any, value: Any):
        """在尾部追加节点，并同步更新索引。"""
        n = Node(key, value)
        self._index[key] = n
        if self._tail is None:
            # 首个节点同时成为 head 和 tail。
            self._head = self._tail = n
        else:
            # 常规尾插：接到当前 tail 后方。
            n.prev = self._tail
            self._tail.next = n
            self._tail = n
