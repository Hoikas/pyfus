#    fus - fast uru server
#    Copyright (C) 2014  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import weakref

def _fetch_ll(item):
    ref = getattr(item, "_ll", None)
    if ref is not None:
        return ref()
    return None

class LinkedList:
    """An intrusive doubly-linked list. If you don't know what it is, Google it."""

    def __init__(self):
        self._head = None
        self._tail = None

    def __del__(self):
        self.clear()

    def append_head(self, item):
        if hasattr(item, "_ll"):
            raise ValueError("Adding an item to LinkedList that is already present in another LinkedList")

        # Set up LL members
        item._ll_next = self._head
        item._ll_prev = None
        item._ll = weakref.ref(self)

        # This is the new head
        self._head = item

    def append_tail(self, item):
        if hasattr(item, "_ll"):
            raise ValueError("Adding an item to LinkedList that is already present in another LinkedList")

        item._ll_prev = self._tail
        item._ll_next = None
        item._ll = weakref.ref(self)

        self._tail = item

    append = append_tail

    def clear(self):
        element = self._head
        while element is not None:
            _next = element._ll_next
            del element._ll
            del element._ll_next
            del element._ll_prev
            element = _next

    def __iter__(self):
        element = self._head
        while element is not None:
            yield element
            element = element._ll_next
        return

    @property
    def head(self):
        return self._head

    @classmethod
    def next(cls, item):
        if not hasattr(item, "_ll"):
            raise ValueError("Item is not a member of any linked list")
        return item._ll_next

    @classmethod
    def prev(cls, item):
        if not hasattr(item, "_ll"):
            raise ValueError("Item is not a member of any linked list")
        return item._ll_prev

    @property
    def tail(self):
        return self._tail

    def remove(self, item):
        ll = _fetch_ll(item)
        if ll is None:
            raise ValueError("Item is not a member of any LinkedList")
        elif ll != self:
            raise ValueError("Item is not a member of this LinkedList")

        # Fix links
        if item._ll_prev is not None:
            item._ll_prev._ll_next = item._ll_next
        if item._ll_next is not None:
            item._ll_next._ll_prev = item._ll_prev

        # Make sure we don't hold onto the item...
        if self._head == item:
            self._head = item._ll_next
        if self._tail == item:
            self._tail = item._ll_prev

        # Remove
        del item._ll
        del item._ll_prev
        del item._ll_next
