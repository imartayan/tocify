#!/usr/bin/python3

from argparse import ArgumentParser
from subprocess import run

parser = ArgumentParser(description="A tool for writing outline to pdf or djvu files")
parser.add_argument("toc", help="table of contents")
parser.add_argument("file", help="pdf or djvu file")
parser.add_argument("--clean", help="clean outline", action="store_true")
parser.add_argument("--offset", metavar="n", help="add offset", default=0, type=int)
args = parser.parse_args()


class Tree:
    def __init__(self, title, page, parent=None):
        self.depth = -1
        self.title = title
        self.page = page
        self.children = []
        self.parent = None
        if parent:
            assert isinstance(parent, Tree)
            self.parent = parent

    def __repr__(self):
        return self.title

    def add_child(self, title, page):
        node = Tree(title, page, self)
        self.children.append(node)
        node.depth = self.depth + 1
        return node


def clean_line(l):
    num_dots = 0
    num_space = 0
    res = ""
    for c in l:
        if c == ".":
            num_dots += 1
        elif c == " ":
            num_space += 1
        else:
            if num_dots <= 3:
                res += "." * num_dots
            if num_space >= 1:
                res += " "
            res += c
            num_dots = 0
            num_space = 0
    return res


def count_indent(s, tab="\t"):
    k = len(tab)
    c = 0
    i = 0
    while s[i : i + k] == tab:
        c += 1
        i += k
    return c


def get_title_page(line):
    L = line.split()
    try:
        page = int(L.pop())
        title = " ".join(L)
        return title, page
    except Exception as e:
        print(e)


def create_tree(toc, offset=0):
    root = Tree("root", 0)
    last_node = root
    last_depth = -1
    with open(toc, "r") as f:
        for l in f:
            s = clean_line(l)
            depth = count_indent(s)
            title, page = get_title_page(s)
            page += offset
            node = last_node
            while depth <= last_depth:
                node = node.parent
                last_depth -= 1
            last_node = node.add_child(title, page)
            last_depth = depth
    return root


def export_tree_clean(tree, out):
    lines = []

    def walk(node):
        if node.depth >= 0:
            line = "\t" * node.depth
            line += node.title + " "
            line += str(node.page) + "\n"
            lines.append(line)
        if node.children:
            for child in node.children:
                walk(child)

    walk(tree)

    with open(out, "w") as f:
        f.writelines(lines)


def export_tree_pdf(tree, out):
    lines = []

    def walk(node):
        if node.depth >= 0:
            line = str(node.depth) + " "
            line += '"' + node.title + '" '
            line += str(node.page) + "\n"
            lines.append(line)
        if node.children:
            for child in node.children:
                walk(child)

    walk(tree)

    with open(out, "w") as f:
        f.writelines(lines)


def export_tree_djvu(tree, out):
    lines = []

    def walk(node):
        if node.depth < 0:
            line = "(bookmarks"
            lines.append(line)
        else:
            line = " " * node.depth
            line += '("' + node.title + '"\n'
            line += " " * (node.depth + 1)
            line += '"#' + str(node.page) + '"'
            lines.append(line)
        if node.children:
            for child in node.children:
                lines.append("\n")
                walk(child)
        lines.append(" )")

    walk(tree)

    with open(out, "w") as f:
        f.writelines(lines)


def get_extension(filename):
    L = filename.split(".")
    return L[-1]


def add_suffix(filename, suffix):
    L = filename.split(".")
    if len(L) > 1:
        L[-2] += suffix
    else:
        L[-1] += suffix
    return ".".join(L)


tree = create_tree(args.toc, args.offset)
if args.clean:
    toc_clean = add_suffix(args.toc, "_clean")
    export_tree_clean(tree, toc_clean)

ext = get_extension(args.file)
assert ext in {"pdf", "djvu"}

if ext == "pdf":
    toc_pdf = add_suffix(args.toc, "_pdf")
    export_tree_pdf(tree, toc_pdf)
    out = add_suffix(args.file, "_out")
    cmd = f"cpdf -add-bookmarks {toc_pdf} {args.file} -o {out}"
    run(cmd, shell=True)
elif ext == "djvu":
    toc_djvu = add_suffix(args.toc, "_djvu")
    export_tree_djvu(tree, toc_djvu)
    cmd = f'djvused -e "set-outline {toc_djvu}" -s {args.file}'
    run(cmd, shell=True)
