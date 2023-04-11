from clang.cindex import *



Config.set_library_file('/usr/local/lib/libclang.so');

index = Index.create()
tu = index.parse('example.cpp');

for node in tu.cursor.walk_preorder():
    if node.kind == CursorKind.FUNCTION_DECL:
        name = node.spelling
        location = node.location
        print('Function {name} is defined at line {location.line}')

print(32)