import os
import re
import sys
import ast
import argparse
from collections import defaultdict


class CodeAnalyzerVisitor(ast.NodeVisitor):
    def __init__(self, filename, output_list):
        self.filename = filename
        self.output_list = output_list

    def visit_ClassDef(self, node):
        class_name = node.name
        if not re.match(r"[A-Z][a-zA-Z0-9]*$", class_name):
            self.output_list.append(f"{self.filename}: Line {node.lineno}: S008 Class name should use CamelCase")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        function_name = node.name
        if not re.match(r"[_a-z][_a-zA-Z0-9]*$", function_name):
            self.output_list.append(f"{self.filename}: Line {node.lineno}: S009 Function name should use snake_case")
        self.generic_visit(node)


class CodeAnalyzer:
    def __init__(self):
        self.stats = {
            "variables": defaultdict(list),
            "parameters": defaultdict(list),
            "is_constant_default": defaultdict(list),
        }

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.stats["variables"][node.lineno].append(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for a in node.args.args:
            self.stats["parameters"][node.lineno].append(a.arg)
        for a in node.args.defaults:
            self.stats["is_constant_default"][node.lineno].append(isinstance(a, ast.Constant))
        self.generic_visit(node)

    def get_parameters(self, lineno):
        return self.stats["parameters"][lineno]

    def get_variables(self, lineno):
        return self.stats["variables"][lineno]

    def get_mutable_defaults(self, lineno):
        for param_name, is_default in zip(self.stats["parameters"][lineno], self.stats["is_constant_default"][lineno]):
            if not is_default:
                return param_name
        return ""


def input_path():
    args = sys.argv
    if len(args) < 2:
        return
    if not os.path.exists(args[1]):
        return
    return args[1]


def analyze_pathname(pathname):
    if not pathname:
        return
    if os.path.isfile(pathname):
        return analyze_file(pathname)
    if os.path.isdir(pathname):
        scripts = sorted(os.listdir(pathname))
        for script in scripts:
            script_path = os.path.join(pathname, script)
            analyze_file(script_path)


def analyze_file(filename):
    counter = 0
    output_list = []

    with open(filename, 'r') as f:
        code = f.read()
        try:
            tree = ast.parse(code)
        except SyntaxError:
            pass
        else:
            visitor = CodeAnalyzerVisitor(filename, output_list)
            visitor.visit(tree)

        f.seek(0)
        for i, line in enumerate(code.splitlines(), start=1):
            if line == "":
                counter += 1
                continue

            error_source = f"{filename}: Line {i}:"

            if len(line) > 79:
                output_list.append(f"{error_source} S001 Too long")

            if not re.match(r"^( {4})*[^ ]", line):
                output_list.append(f"{error_source} S002 Indentation is not a multiple of four")

            if not re.search(r'^\s*#', line) and re.search(r"[^#]*;\s*(#.*)?$", line) and not re.search(
                    r'(["\']).*?;\s*\1', line) and not re.search(r'[^\S;]+\s*;\s*$', line):
                output_list.append(f"{error_source} S003 Unnecessary semicolon")

            if re.search(r"(?i)[^#]*[^ ]( ?#)", line):
                output_list.append(f"{error_source} S004 At least two spaces before inline comment required")

            if re.search(r'(?i)(?<!["\']).*?\bTODO\b', line) and not re.search(r'(["\']).*?\\?\bTODO\b.*?\\?\1', line):
                output_list.append(f"{error_source} S005 TODO found")

            if counter > 2:
                output_list.append(f"{error_source} S006 More than two blank lines used before this line")
            counter = 0

            if re.search(r"(?i)(class|def)\s+\w+\s{3,}", line) or re.search(r"(?i)(class|def)\s+\w+\s{0,1}", line):
                output_list.append(f"{error_source} S007 Too many spaces after 'class' or 'def'")

    flat_list = []
    for item in output_list:
        if type(item) == list:
            flat_list = flat_list + item
        else:
            flat_list.append(item)

    for i in sorted(output_list, key=my_digit_sort()):
        print(i)


def my_digit_sort():
    rx = re.compile(r'(\d+)|(.)')
    def key(x):
        return [(j, int(i)) if i != '' else (j, i)
                for i, j in rx.findall(x)]
    return key


def main():
    analyze_pathname(input_path())
