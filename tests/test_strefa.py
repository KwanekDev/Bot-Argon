import asyncio
import os

from app.core.seeds import seed_defaults
from app.modules.strefa.infrastructure.repositories import (
    SqlAlchemyApplicationRepository,
    SqlAlchemyEventTemplateRepository,
    SqlAlchemyStrefaCommandRepository,
)


async def test_strefa_seeding(db_file):
    url, factory, _ = db_file
    await asyncio.to_thread(_seed_quiet, factory)
    async with factory() as session:
        commands = await SqlAlchemyStrefaCommandRepository(session).list()
        apps = await SqlAlchemyApplicationRepository(session).list()
        events = await SqlAlchemyEventTemplateRepository(session).list()
    names = {c.name for c in commands}
    assert "ankieta-roleplay" in names
    assert "zbanuj" in names
    assert "template" not in names
    assert "permisje" not in names
    assert "stworz-wydarzenie" not in names
    assert len(apps) == 14
    assert len(events) >= 10


def _seed_quiet(factory):
    # re-use seed_defaults with test env (no admin creation)
    os.environ["ENVIRONMENT"] = "test"
    asyncio.run(seed_defaults(factory))

