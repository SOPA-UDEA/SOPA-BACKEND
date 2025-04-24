from prisma import Prisma

database = Prisma(auto_register=True)


async def get_database():
    yield database
