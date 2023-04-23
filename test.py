import clang.cindex
from clang.cindex import *
from typing import List, Dict
from enum import Enum
import copy


class NodeKind(Enum):
    Normal = 1;
    Continue = 2;
    Break = 3;
    Return = 4;
    GOTO = 5;



# -*- coding: utf-8 -*-

Config.set_library_file('/usr/local/lib/libclang.so');
file_name = "test.cpp";
with open(file_name) as f:
    file_contents = f.read();

class CFGNode:
    def __init__(self, id: str, text: str, kind: str):
        self.id = id;
        self.text = text;
        self.kind = kind;

class CFGEdge:
    def __init__(self, begin: str, end: str):
        self.begin = begin;
        self.end = end;

class LastNode:
    def __init__(self, id: str, nodeType: NodeKind, name: str = None):
        self.id = id;
        self.nodeType = nodeType;
        self.name = name;

class CFGData:
    def __init__(self, nodes: List[CFGNode], edges: List[CFGEdge], lastNodes: List[LastNode], specialAndLastNodes: List[LastNode]):
        self.nodes = nodes;
        self.edges = edges;
        self.lastNodes = lastNodes;
        self.specialAndLastNodes = specialAndLastNodes;

    def appendCFGNode(self, node: CFGNode):
        self.nodes.append(node);

    def appendCFGEdge(self, edge: CFGEdge):
        self.edges.append(edge);

    def appendCFGLastNode(self, lastNode: LastNode):
        self.lastNodes.append(lastNode);

    def appendSpecialAndLastNode(self, specialAndLastNode: LastNode):
        self.specialAndLastNodes.append(specialAndLastNode);

    def cleanCFGLastNodes(self):
        self.lastNodes.clear();

    def cleanSpeicalAndLastNodes(self):
        specialAndLastNodes = self.specialAndLastNodes;
        i = 0;

        while i < len(specialAndLastNodes):
            if(NodeKind.Normal == specialAndLastNodes[i].nodeType):
                del specialAndLastNodes[i];
            else:
                i = i + 1;



class CFGBlock(CFGNode):
    def __init__(self, id: str, text: str, kind: str, children: CFGData):
        super().__init__(id, text, kind);
        self.children = children;


class CFGManager:
    def __init__(self, cfgData: CFGData):
        self.cfgData = cfgData;
        self.__lastNodeId = 'null';

    def appendCFGNode(self, node: CFGNode):
        self.cfgData.appendCFGNode(node);


    def appendCFGEdge(self, edge: CFGEdge):
        self.cfgData.appendCFGEdge(edge);

    def appendCFGLastNode(self, lastNode: LastNode):
        self.cfgData.appendCFGLastNode(lastNode);

    def appendSpecialAndLastNode(self, specialAndLastNode: LastNode):
        self.cfgData.appendSpecialAndLastNode(specialAndLastNode);

    def cleanCFGLastNodes(self):
        self.cfgData.cleanCFGLastNodes();

    def getCFGLastNodes(self) -> List[LastNode]:
        return self.cfgData.lastNodes;

    def getSpecialAndLastNode(self) -> List[LastNode]:
        return self.cfgData.specialAndLastNodes;

    def cleanSpecialAndLastNodes(self):
        self.cfgData.cleanSpeicalAndLastNodes();

    def getCFGData(self):
        return self.cfgData;

def getContent(node_cur):
    """获取当前stmt节点对应的代码语句"""
    cursor_content = "";
    for token in node_cur.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        str_token = token.spelling + " ";
        cursor_content = cursor_content + str_token;
    return cursor_content;


def generateAST(file):
    index = Index.create();
    tu = index.parse(file);
    return tu.cursor;

def getStatements(tu_cursor):
    tu_child = tu_cursor.get_children();
    statements = [c for c in tu_child];
    return statements;

# 测试当前节点所有子节点相关信息
def testChildren(current_node):
    print("start---------------------------------------")
    children_statements = getStatements(current_node);
    for node in children_statements:
        nodeId = node.hash;
        kind = node.kind;
        spelling = node.spelling;
        print("hash:", node.hash);
        print("kind:", node.kind);
        print("content",getContent(node));
        print("spelling:", node.spelling);
        print("fileName:", node.location.file.name);

    print("end--------------------------------------");

def disposeIF_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    """处理IFSTMT节点的函数"""
    # 获取孩子节点
    children_statements = getStatements(node);

    testChildren(node);
    length = len(children_statements);

    condition = children_statements[0];

    # 处理condition
    cfgManager.appendCFGNode(CFGNode(str(condition.hash), "if:("+getContent(condition)+")", condition.kind));
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();

    for specialAndLastNode in specialAndLastNodes:
        if (specialAndLastNode.nodeType == NodeKind.Normal):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, condition.hash));

    cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

    # 处理true分支
    trueStmt = [];
    trueStmt.append(children_statements[1]);
    trueStmt_children = generateCFG(trueStmt);

    # 该compound_stmt第一个节点的nodeId
    trueStmt_firstNodeId = trueStmt_children.nodes[0].id;

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();

    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, trueStmt_firstNodeId));

    for child_node in trueStmt_children.nodes:
        cfgManager.appendCFGNode(child_node);

    for child_edge in trueStmt_children.edges:
        cfgManager.appendCFGEdge(child_edge);



    if(length >= 3):
        # 处理false分支
        falseStmt = [];
        falseStmt.append(children_statements[2]);
        falseStmt_children = generateCFG(falseStmt);

        # 该compound_stmt第一个节点的nodeId
        falseStmt_firstNodeId = falseStmt_children.nodes[0].id;

        for specialAndLastNode in specialAndLastNodes:
            if (NodeKind.Normal == specialAndLastNode.nodeType):
                cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, falseStmt_firstNodeId));

        for child_node in falseStmt_children.nodes:
            cfgManager.appendCFGNode(child_node);

        for child_edge in falseStmt_children.edges:
            cfgManager.appendCFGEdge(child_edge);

        # 推入false分支的lastnodes节点
        for child_specialAndLastNode in falseStmt_children.specialAndLastNodes:
            cfgManager.appendSpecialAndLastNode(child_specialAndLastNode);

    # 推入true分支的lastnodes节点
    for child_specialAndLastNode in trueStmt_children.specialAndLastNodes:
        cfgManager.appendSpecialAndLastNode(child_specialAndLastNode);

    # if-end
    cfgManager.appendCFGNode(CFGNode(str(condition.hash)+"end", "if-end", "if-end"));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();

    for specialAndLastNode in specialAndLastNodes:
        if (NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, str(condition.hash)+"end"));

    cfgManager.appendSpecialAndLastNode(LastNode(str(condition.hash)+"end", NodeKind.Normal));

def disposeRETURN_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    """处理RETURN_STMT节点的函数"""
    nodeId = node.hash;
    source_text = getContent(node);
    print("source_text:", source_text);

    cfgManager.appendCFGNode(CFGNode(nodeId, source_text, node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if (specialAndLastNode.nodeType == NodeKind.Normal):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    # cfgManager.appendCFGLastNode(LastNode(node.hash, NodeKind.Return));
    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Return));

def disposeCOMPOUND_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
   """处理COMPOUND_STMT节点的函数"""
   statements = getStatements(node);
   testChildren(node);

   children = generateCFG(statements);

   # 该compound_stmt第一个节点的nodeId
   firstNodeId = children.nodes[0].id;

   specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
   cfgManager.cleanSpecialAndLastNodes();

   for specialAndLastNode in specialAndLastNodes:
       if (specialAndLastNode.nodeType == NodeKind.Normal):
           cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, firstNodeId));


   for child_node in children.nodes:
       cfgManager.appendCFGNode(child_node);

   for child_edge in children.edges:
       cfgManager.appendCFGEdge(child_edge);

   for specialAndLastNode in children.specialAndLastNodes:
       cfgManager.appendSpecialAndLastNode(specialAndLastNode);

def disposeFUNCTION_DECL(node:clang.cindex.Cursor, cfgManager: CFGManager):
    """处理FUNCTION_DECL节点的函数"""

    if (CursorKind.FUNCTION_DECL == node.kind and node.location.file.name == file_name):

        children_statements = getStatements(node);
        specialAndLastNodes = cfgManager.getSpecialAndLastNode();

        if (len(children_statements) != 0):
            if (CursorKind.COMPOUND_STMT == children_statements[-1].kind):
                testChildren(children_statements[-1]);
                # disposeCOMPOUND_STMT(children_statements[-1]);
                # 这个暂时作过度用，获取compound_stmt的children节点
                temp_statements = getStatements(children_statements[-1]);
                children = generateCFG(temp_statements);

                if (len(children.nodes) > 0):
                    children.edges.append(CFGEdge("[*]", children.nodes[0].id));

                    for specialAndLastNode in children.specialAndLastNodes:
                        if(specialAndLastNode.nodeType != NodeKind.GOTO):
                            children.edges.append(CFGEdge(specialAndLastNode.id, "[*]"));

                block = CFGBlock(node.hash, node.spelling, node.kind, children);
                cfgManager.appendCFGNode(block);

                for specialAndLastNode in specialAndLastNodes:
                    cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

                cfgManager.cleanSpecialAndLastNodes();
                cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));

def disposeOther_Node(node: clang.cindex.Cursor, cfgManager:CFGManager):
    """处理非特殊AST节点的函数"""

    nodeId = node.hash;
    source_text = getContent(node);
    print("source_text:", source_text);

    cfgManager.appendCFGNode(CFGNode(nodeId, source_text, node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(specialAndLastNode.nodeType == NodeKind.Normal):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));

def getFOR_STMT_STRUCT(node: clang.cindex.Cursor)-> []:
    # 获取for循环的结构(因为有for(;;i++)这种的情况
    # 判断是否存在
    struct_judge = [False, False, False];
    index = 0;
    tokens = node.get_tokens();
    it = node.get_tokens();
    it_iterator = iter(it);
    next(it_iterator);
    for i in tokens:
        try:
            nextToken = next(it_iterator);
        except StopIteration:
            pass;
        if (index == 0):
            if (str(i.spelling) == '('):
                if (str(nextToken.spelling) != ';'):
                    struct_judge[index] = True;
                    index += 1;
                else:
                    index += 1;
        if (index == 1 or index == 2):
            if (str(i.spelling) == ';'):
                if (str(nextToken.spelling) != ';' and str(nextToken.spelling) != ')'):
                    struct_judge[index] = True;
                    index += 1;
                else:
                    index += 1;
        if (str(i.spelling) == '{'):
            break;

    return struct_judge;

def disposeFOR_STMT(node: clang.cindex.Cursor, cfgManager: CFGManager):
    """处理FOR_STMT节点的函数"""
    testChildren(node);
    statements = getStatements(node);
    testChildren(statements[-1]);
    length = len(statements);



    initializer = None;
    condition = None;
    incrementor = None;

    struct_judge = getFOR_STMT_STRUCT(node);

    # 获取initializer
    if (struct_judge[0] == True):
        initializer = statements[0];

    # 获取condition
    if (struct_judge[1] == True):
        if (struct_judge[0] == True):
            condition = statements[1];
        else:
            condition = statements[0];

    # 获取increamentor
    if (struct_judge[2] == True):
        if (struct_judge[1] == True and struct_judge[0] == True):
            incrementor = statements[2];
        elif ((struct_judge[0] == False and struct_judge[1] == True) or
              (struct_judge[0] == True and struct_judge[1] == False)):
            incrementor = statements[1];
        elif (struct_judge[0] == False and struct_judge[1] == False):
            incrementor = statements[0];

    # 获取body
    compound_statements = statements[-1];

    # 推入for-begin
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    cfgManager.appendCFGNode(CFGNode(node.hash, 'for-begin', node.kind));
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));
    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));

    # 推入initializer
    if(initializer is not None):
        specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
        cfgManager.cleanSpecialAndLastNodes();
        spelling = getContent(initializer);
        cfgManager.appendCFGNode(CFGNode(initializer.hash,'for initializer:'+ getContent(initializer), initializer.kind));
        for specialAndLastNode in specialAndLastNodes:
            if(NodeKind.Normal == specialAndLastNode.nodeType):
                cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, initializer.hash));
        cfgManager.appendSpecialAndLastNode(LastNode(initializer.hash, NodeKind.Normal));

    # 推入condition
    if (condition is not None):
        specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
        cfgManager.cleanSpecialAndLastNodes();
        cfgManager.appendCFGNode(CFGNode(condition.hash, 'for condition:' + getContent(condition), condition.kind));
        for specialAndLastNode in specialAndLastNodes:
            if (NodeKind.Normal == specialAndLastNode.nodeType):
                cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, condition.hash));
        cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

    disposeLoop(compound_statements, cfgManager, incrementor);

    # 推入incrementor
    if(incrementor is not None):
        cfgManager.appendCFGNode(CFGNode(incrementor.hash, 'for incrementor:'+getContent(incrementor), incrementor.kind));


    # increamentor到condition的边
    cfgManager.appendCFGEdge(CFGEdge(incrementor.hash, condition.hash));

    # 推入condition到last_nodes
    cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

def disposeBREAK_STMT(node:clang.cindex.Cursor, cfgManager:CFGManager):
    """处理BREAK_STMT节点的函数"""
    nodeId = node.hash;
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    for specialAndLastNode in specialAndLastNodes:
        if (specialAndLastNode.nodeType == NodeKind.Normal):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    cfgManager.cleanSpecialAndLastNodes();
    cfgManager.appendCFGNode(CFGNode(nodeId, 'BREAK', node.kind));
    cfgManager.appendSpecialAndLastNode(LastNode(nodeId, NodeKind.Break));

def disposeCONTINUE_STMT(node:clang.cindex.Cursor, cfgManager:CFGManager):
    """处理CONTINUE_STMT节点的函数"""
    nodeId = node.hash;
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if (specialAndLastNode.nodeType == NodeKind.Normal):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    cfgManager.appendCFGNode(CFGNode(nodeId, 'CONTINUE', node.kind));
    cfgManager.appendSpecialAndLastNode(LastNode(nodeId, NodeKind.Continue));

def disposeLoop(node:clang.cindex.Cursor, cfgManager:CFGManager, nextDoNode:clang.cindex.Cursor):
    """处理所有跟循环有关的body"""
    statements = [];
    statements.append(node);
    children = generateCFG(statements);

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();

    if(len(children.nodes) > 0 ):
        for specialAndLastNode in specialAndLastNodes:
            if(NodeKind.Normal == specialAndLastNode.nodeType):
                cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, children.nodes[0].id));

        for node in children.nodes:
            cfgManager.appendCFGNode(node);

        for edge in children.edges:
            cfgManager.appendCFGEdge(edge);

        for specialAndLastNode in children.specialAndLastNodes:
            if(NodeKind.Break == specialAndLastNode.nodeType):
                continue;

            if(NodeKind.Return == specialAndLastNode.nodeType):
                continue;

            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, nextDoNode.hash));


        for specialAndLastNode in children.specialAndLastNodes:
            if(NodeKind.Break == specialAndLastNode.nodeType):
                cfgManager.appendSpecialAndLastNode(LastNode(specialAndLastNode.id, NodeKind.Normal));
            elif(NodeKind.Return == specialAndLastNode.nodeType):
                cfgManager.appendSpecialAndLastNode(LastNode(specialAndLastNode.id, NodeKind.Return));
            # elif(NodeKind.Break != specialAndLastNode.nodeType and NodeKind.Continue != specialAndLastNode.nodeType and NodeKind.Normal != specialAndLastNode.nodeType):
            #     cfgManager.appendSpecialAndLastNode(specialAndLastNode);

def disposeWHILE_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    testChildren(node);
    statements = getStatements(node);

    # 获取条件
    condition = statements[0];

    # 获取body
    compound_body = statements[-1];

    # condition
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, condition.hash));

    cfgManager.appendCFGNode(CFGNode(condition.hash, 'while(' + getContent(condition) + ')', condition.kind));
    cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

    #处理循环
    disposeLoop(compound_body, cfgManager, condition);

    cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

    # while-end
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(str(specialAndLastNode.id), str(node.hash)+"end"));
    cfgManager.appendCFGNode(CFGNode(str(node.hash)+"end", "while-end", "while-end"));

    cfgManager.appendSpecialAndLastNode(LastNode(str(node.hash)+"end", NodeKind.Normal));

def disposeDO_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    """处理do_while节点的函数"""
    statements = getStatements(node);

    condition = statements[-1];
    compound_body = statements[0];

    # do
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));
    cfgManager.appendCFGNode(CFGNode(node.hash, 'do', node.kind));
    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));

    # 处理condition
    cfgManager.appendCFGNode(CFGNode(condition.hash, 'while('+getContent(condition)+')', condition.kind));
    cfgManager.appendCFGEdge(CFGEdge(condition.hash, node.hash));


    # 处理body
    disposeLoop(compound_body, cfgManager, condition);

    cfgManager.appendSpecialAndLastNode(LastNode(condition.hash, NodeKind.Normal));

    # do-end
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if (NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(str(specialAndLastNode.id), str(node.hash) + "end"));
    cfgManager.appendCFGNode(CFGNode(str(node.hash) + "end", "do-end", "do-end"));

    cfgManager.appendSpecialAndLastNode(LastNode(str(node.hash) + "end", NodeKind.Normal));

def disposeCXX_FOR_RANGE_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    statements = getStatements(node);

    # for(x:y)
    cfgManager.appendCFGNode(CFGNode(node.hash, f"{getContent(statements[0])} {getContent(statements[1])}", node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));
    disposeLoop(statements[-1], cfgManager, node);

    cfgManager.appendSpecialAndLastNode(LastNode(node.hash, NodeKind.Normal));

def disposeCASE_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    testChildren(node);

    statements = getStatements(node);
    real_statements = [];

    for i in range(len(statements)):
        if i != 0:
            real_statements.append(statements[i]);

    testChildren(node);
    children = generateCFG(real_statements);

    # 处理并标记成case：xx
    cfgManager.appendCFGNode(CFGNode(node.hash, f"case {getContent(statements[0])}", node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    cfgManager.appendCFGEdge(CFGEdge(node.hash, children.nodes[0].id));


    for children_node in children.nodes:
        cfgManager.appendCFGNode(children_node);

    for children_edge in children.edges:
        cfgManager.appendCFGEdge(children_edge);



    # # 推入case_end
    # cfgManager.appendCFGNode(CFGNode(f"{firstNode.hash}end", f"case {getContent(firstNode)} -end", "case-end"));

    for children_specialAndLastNode in children.specialAndLastNodes:
        # if(NodeKind.Break == children_specialAndLastNode.nodeType or NodeKind.Normal == children_specialAndLastNode.nodeType):
        #     cfgManager.appendCFGEdge(CFGEdge(f"{children_specialAndLastNode.id}", f"{firstNode.hash}end"));
        #     continue;
        cfgManager.appendSpecialAndLastNode(children_specialAndLastNode);

    # cfgManager.appendSpecialAndLastNode(LastNode(f"{firstNode.hash}end", NodeKind.Normal));




    print(32);

def disposeDEFAULT_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    testChildren(node);

    statements = getStatements(node);
    children = generateCFG(statements);

    # 处理并标记成default-begin

    cfgManager.appendCFGNode(CFGNode(node.hash, "default", node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if (NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

   # 与返回来的children nodes首节点链接
    cfgManager.appendCFGEdge(CFGEdge(node.hash, children.nodes[0].id));

    for children_node in children.nodes:
        cfgManager.appendCFGNode(children_node);

    for children_edge in children.edges:
        cfgManager.appendCFGEdge(children_edge);

    # 推入default_end
    cfgManager.appendCFGNode(CFGNode(f"{node.hash}end", f"default-end", "default-end"));

    for children_specialAndLastNode in children.specialAndLastNodes:
        if (NodeKind.Break == children_specialAndLastNode.nodeType or NodeKind.Normal == children_specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(f"{children_specialAndLastNode.id}", f"{node.hash}end"));
            continue;
        cfgManager.appendSpecialAndLastNode(children_specialAndLastNode);

    cfgManager.appendSpecialAndLastNode(LastNode(f"{node.hash}end", NodeKind.Normal));

def disposeSWITCH_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    statements = getStatements(node);
    testChildren(node);
    # switch-begin
    cfgManager.appendCFGNode(CFGNode(node.hash, f"switch ( {getContent(statements[0])} )", node.kind));
    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));

    # switch的body
    switch_body = [];
    switch_body.append(statements[-1]);
    children = generateCFG(switch_body);

    for children_node in children.nodes:
        if(CursorKind.CASE_STMT == children_node.kind or CursorKind.DEFAULT_STMT == children_node.kind):
            cfgManager.appendCFGEdge(CFGEdge(node.hash, children_node.id));
        cfgManager.appendCFGNode(children_node);

    for children_edge in children.edges:
        cfgManager.appendCFGEdge(children_edge);

    for specialAndLastNode in children.specialAndLastNodes:
        if(NodeKind.Continue == specialAndLastNode.nodeType or NodeKind.Return == specialAndLastNode.nodeType):
            cfgManager.appendSpecialAndLastNode(specialAndLastNode);
            continue;

        cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, f"{node.hash}end"));

    # 推入switch-end
    cfgManager.appendCFGNode(CFGNode(f"{node.hash}end", "switch-end", "switch-end"));
    cfgManager.appendSpecialAndLastNode(LastNode(f"{node.hash}end", NodeKind.Normal));

def disposeCXX_TRY_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    testChildren(node);
    statements = getStatements(node);
    testChildren(statements[0]);


    # test = [];
    # test.append(statements[1]);
    # generateCFG(test);
    # try-begin

    # specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    # cfgManager.cleanSpecialAndLastNodes();
    #
    # for specialAndLastNode in specialAndLastNodes:
    #     if(NodeKind.Normal == specialAndLastNode.nodeType):
    #         cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));
    #
    # cfgManager.appendCFGNode(CFGNode(node.hash, "try-begin", node.kind));
    #
    # try_body = [];
    # catch_statments = [];
    #
    # for i in range(len(statements)):
    #     if(0 == i):
    #         try_body.append(statements[i]);
    #     else:
    #         catch_statments.append(statements[i]);
    #
    # # 处理try_body
    # try_body_children = generateCFG(try_body);

def disposeCXX_CATCH_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    testChildren(node);
    print(32);

def disposeLABEL_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):

    cfgManager.appendCFGNode(CFGNode(node.hash, f"Label: {node.spelling}", node.kind));

    specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
    cfgManager.cleanSpecialAndLastNodes();
    for specialAndLastNode in specialAndLastNodes:
        spelling = node.spelling;
        name = specialAndLastNode.name;
        if(NodeKind.Normal == specialAndLastNode.nodeType):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));
            continue;
        if(NodeKind.GOTO == specialAndLastNode.nodeType and str(node.spelling) == str(specialAndLastNode.name)):
            cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, node.hash));
            specialAndLastNode.name = None;
            continue;

    # 处理这个label的body
    statements = getStatements(node);
    children = generateCFG(statements);

    if(len(children.nodes) > 0):
        cfgManager.appendCFGEdge(CFGEdge(node.hash, children.nodes[0].id));

    for children_node in children.nodes:
        cfgManager.appendCFGNode(children_node);

    for children_edge in children.edges:
        cfgManager.appendCFGEdge(children_edge);

    for specialAndLastNode in children.specialAndLastNodes:
        cfgManager.appendSpecialAndLastNode(specialAndLastNode);



def disposeGOTO_STMT(node:clang.cindex.Cursor, cfgManager: CFGManager):
    statements = getStatements(node);

    if(len(statements) > 0 ):
        if(CursorKind.LABEL_REF == statements[0].kind):
            cfgManager.appendCFGNode(CFGNode(statements[0].hash, f"goto {getContent(statements[0])}", node.kind));

            specialAndLastNodes = copy.deepcopy(cfgManager.getSpecialAndLastNode());
            cfgManager.cleanSpecialAndLastNodes();
            for specialAndLastNode in specialAndLastNodes:
                if(NodeKind.Normal == specialAndLastNode.nodeType):
                    cfgManager.appendCFGEdge(CFGEdge(specialAndLastNode.id, statements[0].hash));

            goto_name = getContent(statements[0]).replace(" ", "");
            cfgManager.appendSpecialAndLastNode(LastNode(statements[0].hash, NodeKind.GOTO, goto_name));


def visit(node:clang.cindex.Cursor, cfgManager: CFGManager):

    if(CursorKind.IF_STMT == node.kind):
        disposeIF_STMT(node, cfgManager);
        return;

    # if(CursorKind.BINARY_OPERATOR == node.kind):
    #     disposeBINARY_OPERATOR(node, cfgManager);
    #
    # if (CursorKind.UNEXPOSED_EXPR == node.kind):
    #     disposeUNEXPOSED_EXPR(node, cfgManager);

    if(CursorKind.RETURN_STMT == node.kind):
        disposeRETURN_STMT(node, cfgManager);
        return;

    if(CursorKind.BREAK_STMT == node.kind):
        disposeBREAK_STMT(node, cfgManager);
        return;

    if(CursorKind.CONTINUE_STMT == node.kind):
        disposeCONTINUE_STMT(node, cfgManager);
        return;
    # if (CursorKind.DECL_STMT == node.kind):
    #     disposeDECL_STMT(node, cfgManager);
    if(CursorKind.SWITCH_STMT == node.kind):
        disposeSWITCH_STMT(node, cfgManager);
        return;

    if(CursorKind.CASE_STMT == node.kind):
        disposeCASE_STMT(node, cfgManager);
        return;

    if(CursorKind.DEFAULT_STMT == node.kind):
        disposeDEFAULT_STMT(node, cfgManager);
        return;

    if(CursorKind.COMPOUND_STMT == node.kind):
        disposeCOMPOUND_STMT(node, cfgManager);
        return;

    if(CursorKind.FUNCTION_DECL == node.kind):
        disposeFUNCTION_DECL(node, cfgManager);
        return;

    if(CursorKind.CXX_FOR_RANGE_STMT == node.kind):
        disposeCXX_FOR_RANGE_STMT(node, cfgManager);
        return;
    # if(CursorKind.NULL_STMT == node.kind):
    #     disposeNULL_STMT(node, cfgManager);

    if(CursorKind.FOR_STMT == node.kind):
        disposeFOR_STMT(node, cfgManager);
        return;

    if(CursorKind.WHILE_STMT == node.kind):
        disposeWHILE_STMT(node, cfgManager);
        return;

    if(CursorKind.DO_STMT == node.kind):
        disposeDO_STMT(node, cfgManager);
        return;

    if(CursorKind.CXX_TRY_STMT == node.kind):
        disposeCXX_TRY_STMT(node, cfgManager);
        return;

    if(CursorKind.CXX_CATCH_STMT == node.kind):
        disposeCXX_CATCH_STMT(node, cfgManager);
        return;

    if(CursorKind.LABEL_STMT == node.kind):
        disposeLABEL_STMT(node, cfgManager);
        return;

    if(CursorKind.GOTO_STMT == node.kind):
        disposeGOTO_STMT(node, cfgManager);
        return;
    # if(CursorKind.VAR_DECL == node.kind):
    #     type = clang.getTypeDeclaration(node);
    #     print(clang.getTypeSpelling(type));

    if(node.location.file.name == file_name):
        disposeOther_Node(node, cfgManager);

def generateCFG(statements):
    print("len：", len(statements));

    # if(len(statements) == 0):
    #     return answer(nodes = [], edges":[], "last_nodes":[], "specialAndLastNodes");


    nodes: List[CFGNode] = [];
    edges: List[CFGEdge] = [];
    last_nodes: List[LastNode] = [];
    specialAndLastNodes: List[LastNode] = [];

    # 储存CFG数据
    cfgData = CFGData(nodes, edges, last_nodes, specialAndLastNodes);

    cfgManager = CFGManager(cfgData);



    for node in statements:

        nodeId = node.hash;
        kind = node.kind;
        spelling = node.spelling;
        print("hash:", node.hash);
        print("kind:", node.kind);
        print("spelling:", node.spelling);
        print("fileName:",node.location.file.name);

        # if(CursorKind.COMPOUND_STMT == node.kind):

        visit(node, cfgManager);

    return cfgManager.getCFGData();

def add_escape_chars(string:str)-> str:
    string = string.replace('"', '\'');
    return string;

def getMermaid(cfgData: CFGData):
    answer = "stateDiagram-v2\n";

    for node in cfgData.nodes:
        if(type(node) == CFGBlock):
            answer += "state";
            answer = answer + " \"" + add_escape_chars(node.text) + "\" " + "as " + str(
                node.id);
            answer += "{\n";

            # 处理节点
            for children_node in node.children.nodes:
                answer = answer + "state" + " \"" + add_escape_chars(children_node.text) + " \"" + " as " + str(children_node.id) + "\n";

            # 处理边
            for children_edge in node.children.edges:
                answer = answer + str(children_edge.begin) + "-->" + str(children_edge.end) + "\n";

            answer += "}\n";
            continue;
        if(type(node) == CFGNode):
            answer += f"state \"{add_escape_chars(node.text)}\" as {str(node.id)}\n";

    for edge in cfgData.edges:
        answer += f"{str(edge.begin)}-->{str(edge.end)}\n";

    if(len(cfgData.nodes) > 0):
        answer += f"[*]-->{cfgData.nodes[0].id}\n";
        answer += f"{cfgData.nodes[-1].id}-->[*]\n";

    return answer;


def main():
    root_cursor = generateAST(file_name);
    statements = getStatements(root_cursor);
    test = generateCFG(statements);
    answer = getMermaid(test);
    print(answer);


main();