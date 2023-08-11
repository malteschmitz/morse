import tkinter as tk

TREE_LEFT_OFFSET = 10
TREE_LEVEL_DEPTH = 60
TREE_DIAMETER = 25
TREE_LINE_WIDTH = 1.5
TREE_SELECTED_LINE_WITH = 2.5
TREE_SIBLING_DISTANCE = lambda level: 2**max(5-level, 0)*29
TREE_INIT_Y = 480
TREE_DRAW = "black"
TREE_SELECTED_DRAW = "red"
TREE_FILL = "light blue"
TREE_EMPTY_FILL = "light gray"
TREE_SELECTED_FILL = "light pink"
TREE_FONT = ("DejaVu Sans Mono",18)

class Node:
    def __init__(self, value, dot = None, dash = None):
        self.value = value
        self.dot = dot
        self.dash = dash
        self.oval = None
        self.line = None

class DecodeTree:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=560, height=200, background="white", highlightthickness=0)

        self.root_node = Node("",
            Node("E",
                Node("I",
                    Node("S",
                        Node("H",
                            Node("5"),
                            Node("4")),
                        Node("V",
                        None,
                        Node("3"))),
                    Node("U",
                        Node("F"),
                        Node("",
                            Node("",
                                Node("?"),
                                Node("-")),
                            Node("2")))),
                Node("A",
                    Node("R",
                        Node("L"),
                        Node("",
                            Node("+",
                                None,
                                Node(".")))),
                    Node("W",
                        Node("P",
                            None,
                            Node("",
                                Node("@"))),
                        Node("J",
                            None,
                            Node("1"))))),
            Node("T",
                Node("N",
                    Node("D",
                        Node("B",
                            Node("6",
                                None,
                                Node("-")),
                            Node("=")),
                        Node("X",
                            Node("/"))),
                    Node("K",
                        Node("C",
                            None,
                            Node("",
                                Node(";"))),
                        Node("Y",
                            Node("(",
                                None,
                                Node(")"))))),
                Node("M",
                    Node("G",
                        Node("Z",
                            Node("7"),
                            Node("",
                                None,
                                Node(","))),
                        Node("Q")),
                    Node("O",
                        Node("",
                            Node("8",
                                Node(":"))),
                        Node("",
                            Node("9"),
                            Node("0"))))))

        self.plot_tree(self.root_node, 1, TREE_INIT_Y)

        self.reset()

    def reset(self):
        self.clear()
        self.current_node = self.root_node
        self.mark()

    def clear_tree(self, node):
        if node.oval:
            if node.value:
                self.canvas.itemconfig(node.oval, fill=TREE_FILL)
            else:
                self.canvas.itemconfig(node.oval, fill=TREE_EMPTY_FILL)
            self.canvas.itemconfig(node.oval, outline=TREE_DRAW)
            self.canvas.itemconfig(node.oval, width=TREE_LINE_WIDTH)
        if node.line:
            self.canvas.itemconfig(node.line, fill=TREE_DRAW)
            self.canvas.itemconfig(node.line, width=TREE_LINE_WIDTH)
        if node.dash:
            self.clear_tree(node.dash)
        if node.dot:
            self.clear_tree(node.dot)

    def clear(self):
        self.current_node = None
        self.clear_tree(self.root_node)
    
    def mark(self):
        if self.current_node:
            if self.current_node.oval:
                self.canvas.itemconfig(self.current_node.oval, fill=TREE_SELECTED_FILL)
                self.canvas.itemconfig(self.current_node.oval, outline=TREE_SELECTED_DRAW)
                self.canvas.itemconfig(self.current_node.oval, width=TREE_SELECTED_LINE_WITH)
            if self.current_node.line:
                self.canvas.itemconfig(self.current_node.line, fill=TREE_SELECTED_DRAW)
                self.canvas.itemconfig(self.current_node.line, width=TREE_SELECTED_LINE_WITH)

    def dash(self):
        if self.current_node and self.current_node.dash:
            self.current_node = self.current_node.dash
            self.mark()
        else:
            self.clear()

    def dot(self):
        if self.current_node and self.current_node.dot:
            self.current_node = self.current_node.dot
            self.mark()
        else:
            self.clear()

    def is_char_available(self):
        return self.current_node != self.root_node

    def current_char(self):
        if self.current_node and self.current_node.value:
            return self.current_node.value
        else:
            return None

    def plot_tree(self, node, level, y):
        if node.dot:
            node.dot.line = self.canvas.create_line(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_DIAMETER/2, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_SIBLING_DISTANCE(level)/2 + TREE_DIAMETER/2, dash=(3,3))
            self.plot_tree(node.dot, level + 1, y + TREE_SIBLING_DISTANCE(level)/2)
        if node.dash:
            node.dash.line = self.canvas.create_line(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_DIAMETER/2, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y - TREE_SIBLING_DISTANCE(level)/2 + TREE_DIAMETER/2, dash=(9,3))
            self.plot_tree(node.dash, level + 1, y - TREE_SIBLING_DISTANCE(level)/2)
        node.oval = self.canvas.create_oval(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH, y, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER, y + TREE_DIAMETER)
        if node.value:
            self.canvas.create_text(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER / 2 + 1, y + TREE_DIAMETER / 2 + 1, text=node.value, font=TREE_FONT)
