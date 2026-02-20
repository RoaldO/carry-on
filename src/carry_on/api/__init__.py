"""API module for CarryOn."""

from . import courses as courses
from . import ideas as ideas
from . import index as index
from . import player as player
from . import rounds as rounds
from . import schema as schema
from . import strokes as strokes

from carry_on.container import Container

container = Container()
container.wire(modules=[index, strokes, ideas, courses, rounds, player])
