"""API module for CarryOn."""

from . import ideas as ideas
from . import index as index
from . import schema as schema
from . import strokes as strokes

from carry_on.container import Container

container = Container()
container.wire(modules=[index, strokes, ideas])
