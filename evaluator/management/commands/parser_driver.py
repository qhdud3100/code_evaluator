import sys
import copy
import yaml
from collections import OrderedDict
from pycparser import c_ast, parse_file
from django.core.management import BaseCommand

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
sys.path.extend(['.', '..'])

EXECUTABLE_PATH_PREFIX = '/home/ubuntu/code_evaluator/executables/'
SOURCE_PATH_PREFIX = '/home/ubuntu/code_evaluator/source_codes/'
EXPECTED_OUTPUT_PATH_PREFIX = '/home/ubuntu/code_evaluator/expected_output/'
INPUT_PATH_PREFIX = '/home/ubuntu/code_evaluator/input/'

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        config_path = '/home/ubuntu/code_evaluator/config.yml'
        with open(config_path) as fp:
            yaml_loader, _ = ordered_yaml()
            yml = yaml.load(fp, Loader=yaml_loader)

        parse_check = yml['parseCheck']
        if parse_check['FuncDef'] :
            print('----------------func-defs----------------')
            show_func_defs(SOURCE_PATH_PREFIX + 'macro_example.c', yml['FuncDefDetails']['names'])

        if parse_check['FuncCall'] :
            print('----------------func-calls----------------')
            print(yml['FuncCallDetails']['names'])
            show_func_calls(SOURCE_PATH_PREFIX + 'macro_example.c', yml['FuncCallDetails']['names'][0])

        if parse_check['DeclDef']:
            print('----------------decl-defs----------------')
            show_decl_defs(SOURCE_PATH_PREFIX+'structure_example2.c', yml['DeclDefDetails']['names'])

# A simple visitor for FuncDef nodes that prints the names and
# locations of function definitions.
class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self, funcname, result):
        self.result = result
        self.funcname = funcname

    def visit_FuncDef(self, node):
        # print(node)
        if node.decl.name == self.funcname:
            # print('%s at %s' % (node.decl.name, node.decl.coord))
            self.result[self.funcname] = True

def show_func_defs(filename, funcname):
    # Note that cpp is used. Provide a path to your own cpp or
    # make sure one exists in PATH.
    ast = parse_file(filename, use_cpp=True, cpp_path='/usr/bin/cpp',
                     cpp_args=r'-I/home/ubuntu/code_evaluator/pycparser/utils/fake_libc_include')
    # ast.show()
    result = {}
    for each_func in funcname:
        result[each_func] = False
        v = FuncDefVisitor(each_func, result)
        v.visit(ast)

    return result

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self, funcname, result):
        self.funcname = funcname
        self.result = result

    def visit_FuncCall(self, node):
        if node.name.name == self.funcname:
            # print('%s called at %s' % (self.funcname, node.name.coord))
            self.result[self.funcname] = True

        # Visit args in case they contain more func calls.
        if node.args:
            self.visit(node.args)

def show_func_calls(filename, funcname):
    ast =  parse_file(filename, use_cpp=True, cpp_path='/usr/bin/cpp',
                     cpp_args=r'-I/home/ubuntu/code_evaluator/pycparser/utils/fake_libc_include')
    result = {}
    for each_func in funcname:
        v = FuncCallVisitor(each_func, result)
        v.visit(ast)
    return result

def show_decl_defs(filename, declnames):
    ast = parse_file(filename, use_cpp=True, cpp_path='/usr/bin/cpp',
                     cpp_args=r'-I/home/ubuntu/code_evaluator/pycparser/utils/fake_libc_include')
    flag = 0
    result = {}
    for node in ast.ext:
        if not isinstance(node, c_ast.Typedef) or (isinstance(node, c_ast.Typedef) and node.name == 'memory_order'):
            flag = 1
            continue
        if flag == 0:
            continue

        try:
            expanded = expand_struct_typedef(node, ast,
                                             expand_struct=True,
                                             expand_typedef=True)
        except Exception as e:
            return "Not a valid declaration: " + str(e)

        if expanded.name in declnames :
            result[expanded.name] = True
            print(_explain_decl_node(expanded))

    for name in declnames:
        if name not in result.keys():
            result[name] = False

    return result


def _explain_decl_node(decl_node):
    """ Receives a c_ast.Decl note and returns its explanation in
        English.
    """
    storage = ' '.join(decl_node.storage) + ' ' if decl_node.storage else ''

    return (decl_node.name +
            " is a " +
            storage +
            _explain_type(decl_node.type))


def _explain_type(decl):
    """ Recursively explains a type decl node
    """
    typ = type(decl)
    if typ == c_ast.TypeDecl:
        quals = ' '.join(decl.quals) + ' ' if decl.quals else ''
        return quals + _explain_type(decl.type)
    elif typ == c_ast.Typename or typ == c_ast.Decl:
        return _explain_type(decl.type)
    elif typ == c_ast.IdentifierType:
        return ' '.join(decl.names)
    elif typ == c_ast.PtrDecl:
        quals = ' '.join(decl.quals) + ' ' if decl.quals else ''
        return quals + 'pointer to ' + _explain_type(decl.type)
    elif typ == c_ast.ArrayDecl:
        arr = 'array'
        if decl.dim: arr += '[%s]' % decl.dim.value

        return arr + " of " + _explain_type(decl.type)

    elif typ == c_ast.FuncDecl:
        if decl.args:
            params = [_explain_type(param) for param in decl.args.params]
            args = ', '.join(params)
        else:
            args = ''

        return ('function(%s) returning ' % args +
                _explain_type(decl.type))

    elif typ == c_ast.Struct:
        decls = [_explain_decl_node(mem_decl) for mem_decl in decl.decls]
        members = ', '.join(decls)

        return ('struct%s ' % (' ' + decl.name if decl.name else '') +
                ('containing {%s}' % members if members else ''))


def expand_struct_typedef(cdecl, file_ast,
                          expand_struct=False,
                          expand_typedef=False):
    """Expand struct & typedef and return a new expanded node."""
    decl_copy = copy.deepcopy(cdecl)
    _expand_in_place(decl_copy, file_ast, expand_struct, expand_typedef)
    return decl_copy


def _expand_in_place(decl, file_ast, expand_struct=False, expand_typedef=False):
    """Recursively expand struct & typedef in place, throw RuntimeError if
       undeclared struct or typedef are used
    """
    typ = type(decl)

    if typ in (c_ast.Decl, c_ast.TypeDecl, c_ast.PtrDecl, c_ast.ArrayDecl):
        decl.type = _expand_in_place(decl.type, file_ast, expand_struct,
                                     expand_typedef)

    elif typ == c_ast.Struct:
        if not decl.decls:
            struct = _find_struct(decl.name, file_ast)
            if not struct:
                raise RuntimeError('using undeclared struct %s' % decl.name)
            decl.decls = struct.decls

        for i, mem_decl in enumerate(decl.decls):
            decl.decls[i] = _expand_in_place(mem_decl, file_ast, expand_struct,
                                             expand_typedef)
        if not expand_struct:
            decl.decls = []

        # print(typ)

    elif (typ == c_ast.IdentifierType and
          decl.names[0] not in ('int', 'char')):
        typedef = _find_typedef(decl.names[0], file_ast)
        if not typedef:
            raise RuntimeError('using undeclared type %s' % decl.names[0])

        if expand_typedef:
            return typedef.type
        # print(typ)


    return decl


def _find_struct(name, file_ast):
    """Receives a struct name and return declared struct object in file_ast
    """

    for node in file_ast.ext:
        if (type(node) == c_ast.Decl and
           type(node.type) == c_ast.Struct and
           node.type.name == name):
            return node.type


def _find_typedef(name, file_ast):
    """Receives a type name and return typedef object in file_ast
    """
    for node in file_ast.ext:
        if type(node) == c_ast.Typedef and node.name == name:
            return node


def ordered_yaml():
    """Support OrderedDict for yaml.
    Returns:
        yaml Loader and Dumper.
    """
    try:
        from yaml import CDumper as Dumper
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Dumper, Loader

    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_dict(data.items())

    def dict_constructor(loader, node):
        return OrderedDict(loader.construct_pairs(node))

    Dumper.add_representer(OrderedDict, dict_representer)
    Loader.add_constructor(_mapping_tag, dict_constructor)
    return Loader, Dumper
