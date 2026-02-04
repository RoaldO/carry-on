"""CarryOn - A stroke tracking application."""

import abc

from pymongo.collection import Collection

from . import bootstrap


class MongodbDatabase(abc.ABC):
    # TODO this needs to move to the infrastructure
    @abc.abstractmethod
    def get_ideas(self) -> Collection: ...


class RealMongodbDatabase(MongodbDatabase):
    # TODO this needs to move to the infrastructure
    def get_ideas(self) -> Collection:
        from carry_on.infrastructure.mongodb import get_database

        return get_database().ideas


bootstrap.register(MongodbDatabase, RealMongodbDatabase)
