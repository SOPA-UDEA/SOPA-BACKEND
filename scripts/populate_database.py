# scripts/populate_pensum.py

import asyncio
from src.database import database
from src.modules.pensum.services import insert_pensum_from_excel
from src.modules.subject.services import insert_subject_from_excel

async def main():
    await database.connect()  # Conexión al cliente Prisma
    # await insert_pensum_from_excel()
    # await insert_subject_from_excel() 
    await insert_subject_from_excel() # segunda llamada para leer los prerequisitos
    await database.disconnect()  # Desconexión segura

if __name__ == "__main__":
    asyncio.run(main())