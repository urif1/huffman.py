################################################################################
# huffman.py was created by Uri F. as part of a Thermal Physics exercise       #
# regarding information theory. Thus the code has no purpose of being used as  #
# a module of any kind, and is only meant to serve said purpose. It also       #
# contains some bad coding style and habits in order to save time.             #
# The script receives an English language string, generates a Huffman Code for #
# it and encodes said string.                                                  #
#                                10.05.2022                                    #
################################################################################

from collections import Counter
from typing import Optional, Union
import os
import sys


LEFT = '0'
RIGHT = '1'


class Node:
    _id_counter: int = 0
    _char2bin: dict = {}
    
    def __init__(self, data: Optional[str]=None, frequency: Optional[int]=None,
                 left=None, right=None):
        self._freq: Optionsl[int] = frequency
        self._data: Optional[str] = data
        self._left: Optional[Node] = left
        self._right: Optional[Node] = right
        
        self._id = Node._id_counter
        Node._id_counter += 1
        
    def __str__(self):
        s = '('
        if self._left:
            s += str(self._left) + '<-'
        s += self.data
        if self._right:
            s += '->' + str(self._right)
        s += ')'
        
        return s
        
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def frequency(self) -> int:
        if self._freq:
            return self._freq
        
        freq = 0
        if self._left:
            freq += self._left.frequency
        if self._right:
            freq += self._left.frequency
        
        return freq
        
    @property
    def data(self) -> str:
        if self._data:
            return f"{self._data} ({self.frequency})"
        
        return str(self.frequency)
        
    def get_leaves(self):
        for node in self:
            if node._data:
                yield node
                
    def expected_char_bit_length(self) -> float:
        assert(Node._char2bin)
        expected_value = 0
        total = self.frequency
        for node in self.get_leaves():
            expected_value += len(Node._char2bin[node._data]) * \
                              node.frequency / total
                              
        return expected_value
        
    def generate_edge_list(self) -> list[tuple[str, str, str]]:
        edges = []
        
        if self._right:
            edges.append((self, self._right, RIGHT))
            edges += self._right.generate_edge_list()
        
        if self._left:
            edges.append((self, self._left, LEFT))
            edges += self._left.generate_edge_list()
        
        return edges
        
    def __iter__(self):
        if self._left:
            for node in self._left:
                yield node
        
        yield self
        
        if self._right:
            for node in self._right:
                yield node
                
    def generate_char2bin(self, pre: str="") -> None:
        if self._data:
            Node._char2bin[self._data] = pre
            
        else:
            if self._left:
                self._left.generate_char2bin(pre + LEFT)
            if self._right:
                self._right.generate_char2bin(pre + RIGHT)
                
    def encode(self, s: str) -> str:
        assert(Node._char2bin)
        return ''.join((Node._char2bin[c] for c in s))
        
    def decode(self, bits: str) -> str:
        assert(Node._char2bin)
        decoded = ''
        cur = self
        i = 0
        
        while not cur._data and i < len(bits):
            if bits[i] == LEFT:
                cur = cur._left
            else:
                cur = cur._right
            i += 1
            
            if cur._data:
                decoded += cur._data
                cur = self
                
        return decoded
        
        
def pair_nodes(n1: Union[str, Node], n2: Union[str, Node],
               f1: Optional[int], f2: Optional[int]) -> Node:
    if type(n1) == str:
        n1 = Node(n1, f1)
    if type(n2) == str:
        n2 = Node(n2, f2)
        
    new_node = Node(None, f1 + f2, n1, n2)
    return new_node


def build_huffman_tree(s: str) -> Node:
    c = Counter(s)
    freq2node = {}
    
    for k in c:
        if c[k] not in freq2node:
            freq2node[c[k]] = []
        freq2node[c[k]].append(k)
    
    chars = [None, None]
    freqs = [None, None]
    frequencies = sorted(freq2node.keys(), reverse=True)
    while frequencies:
        f = frequencies.pop()
        freq = freq2node[f]
        while freq:
            chars[0] = freq.pop()
            freqs[0] = f
            if freq:
                chars[1] = freq.pop()
                freqs[1] = f
            else:
                new_freq = min(reversed(frequencies), key=lambda k: abs(k-f))
                chars[1] = freq2node[new_freq].pop()
                freqs[1] = new_freq
                if not freq2node[new_freq]:
                    freq2node.pop(new_freq)
                    frequencies.remove(new_freq)
            
            pair = pair_nodes(*chars, *freqs)
            if not frequencies:
                return pair
                
            if pair.frequency not in freq2node:
                freq2node[pair.frequency] = []
                frequencies.append(pair.frequency)
            freq2node[pair.frequency].append(pair)
        
        freq2node.pop(f)
            
        frequencies.sort(reverse=True)
    
    assert(False)
    
    
def main():
    if len(sys.argv) < 2:
        sys.stderr.write(f"usage: python {__file__.split(os.path.sep)[-1]} \"string\"\n")
        return 1
        
    sentence = sys.argv[1].lower().replace(' ', '_')
    tree = build_huffman_tree(sentence)
    
    for node in tree:
        print(node.id, node.data)
    print("#")
    for edge in tree.generate_edge_list():
        print(edge[0].id, edge[1].id, edge[2])
        
    sys.stderr.write("\nHuffman tree:\n" + str(tree) + '\n')
    tree.generate_char2bin()
    encoded = tree.encode(sentence)
    sys.stderr.write(f"\nEncoded sentence:\n{encoded}\n")
    sys.stderr.write(f"\nRe-decoded sentence:\n{tree.decode(encoded)}\n")
    sys.stderr.write(f"\nAscii length: {8*len(sentence)},\tEncoded length: {len(encoded)}\n")
    sys.stderr.write(f"Expected bit-length of character: {tree.expected_char_bit_length()}\n")
    return 0
    

if __name__ == '__main__':
    main()

