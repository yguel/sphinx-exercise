"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Sphinx Exercise Nodes

:copyright: Copyright 2020-2021 by the Executable Books team, see AUTHORS
:licences: see LICENSE for details
"""

from sphinx.util import logging
from docutils.nodes import Node
from docutils import nodes as docutil_nodes
from sphinx import addnodes as sphinx_nodes
from sphinx.writers.latex import LaTeXTranslator
from .latex import LaTeXMarkup
from sphinx.locale import _


logger = logging.getLogger(__name__)
i18n_logger = logging.getLogger("sphinx-exercise-i18n")
LaTeX = LaTeXMarkup()


# Nodes


class exercise_node(docutil_nodes.Admonition, docutil_nodes.Element):
    gated = False
    def gettext(self):
        text = ""
        # Assume the first title node is the title to be translated.
        for child in self.children:
            if isinstance(child, docutil_nodes.title):
                text = child.astext()
                break
            elif isinstance(child, docutil_nodes.subtitle):
                text = child.astext()
                break
        logger.debug("exercise_node gettext() called; returning: %r", text)
        return text
    
    def astext(self):
        text=self.gettext()
        logger.debug("exercise_node astext() called; returning: %r", text)
        return text

class exercise_enumerable_node(docutil_nodes.Admonition, docutil_nodes.Element):
    gated = False
    resolved_title = False
    def gettext(self):
        # Assume the first title node is the title to be translated.
        for child in self.children:
            if isinstance(child, docutil_nodes.title):
                return child.astext()
            elif isinstance(child, docutil_nodes.subtitle):
                return child.astext()
        return ""
    
    def astext(self):
        return self.gettext()


class exercise_end_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class solution_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False
    def gettext(self):
        # Assume the first title node is the title to be translated.
        for child in self.children:
            if isinstance(child, docutil_nodes.title):
                return child.astext()
            elif isinstance(child, docutil_nodes.subtitle):
                return child.astext()
        return ""
    
    def astext(self):
        return self.gettext()


class solution_start_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False


class solution_end_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False  # TODO: is this required?


class exercise_title(docutil_nodes.title):
    def default_title(self):
        title_text = self.children[0].astext()
        if title_text == "Exercise" or title_text == "Exercise %s":
            return True
        else:
            return False


class exercise_subtitle(docutil_nodes.subtitle):
   pass

class solution_title(docutil_nodes.title):
    def default_title(self):
        title_text = self.children[0].astext()
        if title_text == "Solution to":
            return True
        else:
            return False


class solution_subtitle(docutil_nodes.subtitle):
    pass

class exercise_latex_number_reference(sphinx_nodes.number_reference):
    pass


# Test Node Functions


def is_exercise_node(node):
    return isinstance(node, exercise_node) or isinstance(node, exercise_enumerable_node)


def is_exercise_enumerable_node(node):
    return isinstance(node, exercise_enumerable_node)


def is_solution_node(node):
    return isinstance(node, solution_node)


def is_extension_node(node):
    return (
        is_exercise_node(node)
        or is_exercise_enumerable_node(node)
        or is_solution_node(node)
    )


# Visit and Depart Functions


def visit_exercise_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        label = (
            "\\phantomsection \\label{" + f"exercise:{node.attributes['label']}" + "}"
        )  # TODO: Check this resolves.
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")


def visit_exercise_enumerable_node(self, node: Node) -> None:
    """
    LaTeX Reference Structure is exercise:{label} and resolved by
    exercise_latex_number_reference nodes (see below)
    """
    if isinstance(self, LaTeXTranslator):
        label = (
            "\\phantomsection \\label{" + f"exercise:{node.attributes['label']}" + "}\n"
        )
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_enumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")
        self.body.append("\n")


def visit_solution_node(self, node: Node) -> None:
    """
    Reference Structure is {docname}:{label} and resolved by Sphinx
    """
    if isinstance(self, LaTeXTranslator):
        target_label = node.attributes["label"]
        target_node = self.builder.env.sphinx_exercise_registry[target_label]
        docname = target_node.get("docname")
        label = (
            "\\phantomsection \\label{"
            + f"{docname}:{node.attributes['label']}"
            + "}\n"
        )
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_solution_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")
        self.body.append("\n")


def visit_exercise_latex_number_reference(self, node):
    id = node.get("refid")
    text = node.astext()
    hyperref = r"\hyperref[exercise:%s]{%s}" % (id, text)
    self.body.append(hyperref)
    raise docutil_nodes.SkipNode

## Gettext visit and depart functions

def depart_exercise_latex_number_reference(self, node):
    pass

def gettext_visit_exercise_node(self, node):
    msg = node.gettext()
    i18n_logger.info("→ gettext_visit_exercise_node: %r @ line %s", msg, node.line)
    if msg:
        # lineno lives on the node
        self.add_message(msg, node.line)
    raise docutil_nodes.SkipNode

def gettext_depart_exercise_node(self, node):
    pass

def gettext_visit_exercise_enumerable_node(self, node):
    msg = node.gettext()
    i18n_logger.info("→ gettext_visit_exercise_enumerable_node: %r @ line %s", msg, node.line)
    if msg:
        self.add_message(msg, node.line)
    raise docutil_nodes.SkipNode

def gettext_depart_exercise_enumerable_node(self, node):
    pass

def gettext_visit_solution_node(self, node):
    msg = node.gettext()
    i18n_logger.info("→ gettext_visit_solution_node: %r @ line %s", msg, node.line)
    if msg:
        self.add_message(msg, node.line)
    raise docutil_nodes.SkipNode

def gettext_depart_solution_node(self, node):
    pass