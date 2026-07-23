"""Extract the flowchart graph from aamsfc.md.

The diagram in the cornerstone document is the normative artifact. This module
turns it into an edge list so the invariants can be asserted against it
mechanically instead of by eye.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FENCE_OPEN = re.compile(r"^\s*```\s*mermaid\s*$")
FENCE_CLOSE = re.compile(r"^\s*```\s*$")

SKIP_PREFIXES = (
    "%%", "classDef", "class ", "style ", "linkStyle",
    "flowchart", "graph", "direction", "end",
)

SUBGRAPH = re.compile(r'^\s*subgraph\s+([A-Za-z_][A-Za-z0-9_]*)')

# Arrow forms used in the document, longest first so the alternation does not
# match a prefix of a longer operator.
ARROW = re.compile(
    r"""\s*(?P<arrow>
          -\.\s*"L"\s*\.->      # dotted, labelled
        | --\s*"L"\s*-->        # solid, labelled
        | -\.->                 # dotted
        | -{2,}>                # solid
        | ={2,}>                # thick
    )\s*""",
    re.X,
)

DOTTED = re.compile(r"-\.")
NODE_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
QUOTED = re.compile(r'"[^"]*"')
PIPE_LABEL = re.compile(r"\|[^|]*\|")


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    dotted: bool
    label: str
    subgraph: str
    line: int

    def __str__(self) -> str:
        kind = "-.->" if self.dotted else "-->"
        lab = f' "{self.label}"' if self.label else ""
        return f"{self.src} {kind}{lab} {self.dst}"


@dataclass
class Graph:
    edges: list[Edge] = field(default_factory=list)
    nodes: set[str] = field(default_factory=set)

    def into(self, node: str) -> list[Edge]:
        return [e for e in self.edges if e.dst == node]

    def out_of(self, node: str) -> list[Edge]:
        return [e for e in self.edges if e.src == node]


def _extract_block(text: str) -> tuple[list[str], int]:
    """Return the lines of the first mermaid fence, and its 1-based offset."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if FENCE_OPEN.match(line):
            for j in range(i + 1, len(lines)):
                if FENCE_CLOSE.match(lines[j]):
                    return lines[i + 1 : j], i + 2
            raise ValueError("mermaid fence opened but never closed")
    raise ValueError("no mermaid fence found")


def _leading_id(token: str) -> str | None:
    """A node token always begins with its identifier; shape and label follow."""
    m = NODE_ID.match(token.strip())
    return m.group(0) if m else None


def parse(path: Path) -> Graph:
    block, offset = _extract_block(path.read_text(encoding="utf-8"))
    graph = Graph()
    current = "-"

    for n, raw in enumerate(block, start=offset):
        line = raw.strip()
        if not line or line.startswith(SKIP_PREFIXES):
            sub = SUBGRAPH.match(raw)
            if sub:
                current = sub.group(1)
            continue
        sub = SUBGRAPH.match(raw)
        if sub:
            current = sub.group(1)
            continue

        labels = QUOTED.findall(line)
        masked = QUOTED.sub('"L"', line)
        masked = PIPE_LABEL.sub(' "L" ', masked)
        if not ARROW.search(masked):
            ident = _leading_id(masked)
            if ident:
                graph.nodes.add(ident)
            continue

        parts = ARROW.split(masked)
        # split() with one named group yields: tok, arrow, tok, arrow, tok...
        tokens = parts[0::2]
        arrows = parts[1::2]
        ids = [_leading_id(t) for t in tokens]

        edge_labels = [l.strip('"') for l in labels]
        # Labels attached to arrows are consumed in order; node labels are
        # interleaved but harmless — only arrow-adjacent ones matter and those
        # are the ones sitting inside the arrow operator itself.
        li = 0
        for k, arrow in enumerate(arrows):
            src, dst = ids[k], ids[k + 1]
            if not src or not dst:
                continue
            label = ""
            if '"L"' in arrow:
                # find the label that belongs to this arrow
                if li < len(edge_labels):
                    label = edge_labels[li]
                li += 1
            graph.nodes.update([src, dst])
            graph.edges.append(
                Edge(src, dst, bool(DOTTED.search(arrow)), label, current, n)
            )

    return graph


if __name__ == "__main__":
    import sys

    doc = Path(sys.argv[1] if len(sys.argv) > 1 else "aamsfc.md")
    g = parse(doc)
    print(f"{len(g.nodes)} nodes, {len(g.edges)} edges\n")
    for node in sorted(g.nodes):
        ins = len(g.into(node))
        outs = len(g.out_of(node))
        print(f"  {node:<16} in={ins:<3} out={outs}")
