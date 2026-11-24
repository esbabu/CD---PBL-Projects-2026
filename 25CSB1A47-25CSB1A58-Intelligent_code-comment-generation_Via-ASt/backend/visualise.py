import ast
import numbers
import re
import shutil
from uuid import uuid4 as uuid

import graphviz as gv


def graphviz_available():
    return shutil.which("dot") is not None


def transform_ast(code_ast):
    if isinstance(code_ast, ast.AST):
        node = {
            to_camelcase(k): transform_ast(getattr(code_ast, k))
            for k in code_ast._fields
        }
        node["node_type"] = to_camelcase(code_ast.__class__.__name__)
        return node
    elif isinstance(code_ast, list):
        return [transform_ast(el) for el in code_ast]
    else:
        return code_ast


def to_camelcase(string):
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()


class GraphRenderer:
    """
    this class is capable of rendering data structures consisting of
    dicts and lists as a graph using graphviz
    """

    from typing import ClassVar
    graphattrs: ClassVar[dict[str, str]] = {
        "labelloc": "t",
        "fontcolor": "white",
        "bgcolor": "white",
        "margin": "0",
    }

    nodeattrs: ClassVar[dict[str, str]] = {
        "color": "white",
        "fontcolor": "white",
        "style": "filled",
        "fillcolor": "#006699",
    }

    edgeattrs: ClassVar[dict[str, str]] = {
        "color": "black",
        "fontcolor": "black",
    }

    @staticmethod
    def _escape_dot_label(str):
        return (
            str.replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("<", "\\<")
            .replace(">", "\\>")
        )

    def _render_node(self, node, graph: gv.Digraph, rendered_nodes: set[str]):
        if isinstance(node, (str, numbers.Number)) or node is None:
            node_id = uuid()
        else:
            node_id = id(node)
        node_id = str(node_id)

        if node_id not in rendered_nodes:
            rendered_nodes.add(node_id)
            if isinstance(node, dict):
                self._render_dict(node, node_id, graph, rendered_nodes)
            elif isinstance(node, list):
                self._render_list(node, node_id, graph, rendered_nodes)
            else:
                graph.node(node_id, label=self._escape_dot_label(str(node)))

        return node_id

    def _render_dict(self, node, node_id, graph, rendered_nodes):
        graph.node(node_id, label=node.get("node_type", "[dict]"))
        for key, value in node.items():
            if key == "node_type":
                continue
            child_node_id = self._render_node(value, graph, rendered_nodes)
            graph.edge(node_id, child_node_id)

    def _render_list(self, node, node_id, graph, rendered_nodes):
        graph.node(node_id, label="[list]")
        for value in node:
            child_node_id = self._render_node(value, graph, rendered_nodes)
            graph.edge(node_id, child_node_id)

    def render(self, data, *, label=None):
        # create the graph
        graphattrs = self.graphattrs.copy()
        if label is not None:
            graphattrs["label"] = self._escape_dot_label(label)
        graph = gv.Digraph(
            graph_attr=graphattrs, node_attr=self.nodeattrs, edge_attr=self.edgeattrs
        )

        self._render_node(data, graph, set())

        return graph.pipe(format="pdf")


def open_ast_pdf(code):
    if not graphviz_available():
        raise RuntimeError(
            "AST PDF viewing requires Graphviz's 'dot' executable on PATH. "
            "Install Graphviz, add its bin directory to PATH, and restart the app."
        )

    code_ast = ast.parse(code)
    transformed_ast = transform_ast(code_ast)

    renderer = GraphRenderer()
    return renderer.render(transformed_ast)
