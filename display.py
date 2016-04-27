from tkinter import *

root = Tk()

canvas = Canvas(root, width=500, height=500)
canvas.pack(fill=BOTH,expand=1)

class Node:
  def __init__(self, value, dot = None, dash = None):
    self.value = value
    self.dot = dot
    self.dash = dash

tree = Node("",
        Node("E",
          Node("I",
            Node("S",
              Node("H", Node("5"), Node("4")),
              Node("V", None, Node("3"))),
            Node("U",
              Node("F"),
              Node("Ü", None, Node("2")))),
          Node("A",
            Node("R",
              Node("L"),
              Node("Ä", Node("+"))),
            Node("W",
              Node("P"),
              Node("J", None, Node("1"))))),
        Node("T",
          Node("N",
            Node("D",
              Node("B", Node("6"), Node("=")),
              Node("X", Node("/"))),
            Node("K",
              Node("C"),
              Node("Y"))),
          Node("M",
            Node("G",
              Node("Z", Node("7")),
              Node("Q")),
            Node("O",
              Node("Ö", Node("8")),
              Node("CH", Node("9"), Node("0"))))))

LEFT_OFFSET = 10
LEVEL_DEPTH = 60
DIAMETER = 22
LINE_WIDTH = 1.5
SIBLING_DISTANCE = lambda level: 2**max(5-level, 0)*25
INIT_Y = 500

def plot(node, level, y):
  if node.dot != None:
    node.dot.line = canvas.create_line(LEFT_OFFSET + level * LEVEL_DEPTH + DIAMETER/2, y + DIAMETER/2, LEFT_OFFSET + level * LEVEL_DEPTH + LEVEL_DEPTH + DIAMETER/2, y + SIBLING_DISTANCE(level)/2 + DIAMETER/2, width=LINE_WIDTH, dash=(3,3))
    plot(node.dot, level + 1, y + SIBLING_DISTANCE(level)/2)
  if node.dash != None:
    node.dash.line = canvas.create_line(LEFT_OFFSET + level * LEVEL_DEPTH + DIAMETER/2, y + DIAMETER/2, LEFT_OFFSET + level * LEVEL_DEPTH + LEVEL_DEPTH + DIAMETER/2, y - SIBLING_DISTANCE(level)/2 + DIAMETER/2, width=LINE_WIDTH, dash=(9,3))
    plot(node.dash, level + 1, y - SIBLING_DISTANCE(level)/2)
  node.oval = canvas.create_oval(LEFT_OFFSET + level * LEVEL_DEPTH, y, LEFT_OFFSET + level * LEVEL_DEPTH + DIAMETER, y + DIAMETER, width=LINE_WIDTH, fill="white")
  canvas.create_text(LEFT_OFFSET + level * LEVEL_DEPTH + DIAMETER / 2, y + DIAMETER / 2, text=node.value, font=("DejaVu Sans Mono",18))

plot(tree, 1, INIT_Y)

current_node = tree
canvas.itemconfig(current_node.oval, fill="light pink")

def decode(string):
  global current_node
  if len(string) > 0:
    char = string[0]
    if char == '-':
      current_node = current_node.dash
    else:
      current_node = current_node.dot
    canvas.itemconfig(current_node.oval, fill="light pink")
    canvas.itemconfig(current_node.line, fill="red")
    decode(string[1:])

decode("-.-.")

root.mainloop()