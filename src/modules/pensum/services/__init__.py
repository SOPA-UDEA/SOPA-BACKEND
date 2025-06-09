from src.database import database
import pandas as pd
from src.modules.pensum.models import PensumResponse

async def get_all_pensums():
    return await database.pensum.find_many()

async def get_pensum_by_id(pensumId: int) -> PensumResponse:
    return await database.pensum.find_first(where={"id": pensumId},
                                             include={"academic_program": True})

async def get_pensum_by_version_and_program_id(version, programId):
    return await database.pensum.find_first(where={"version": version, "academicProgramId": programId})

async def insert_pensum_from_excel():
    
    # Carga el archivo Excel
    df = pd.read_excel(r"D:\Escritorio\2.PensumIngSistemas.xlsx", engine="openpyxl")

    # Renombra las columnas
    df = df.rename(columns={
        "VERSION": "version",
        "PROGRAMA": "program_code"
    })

    # Simula un mapeo código -> ID (esto deberías consultarlo de la BD realmente)
    program_lookup = {
        504: 1,
        506: 2,
        552: 3
    }

     # Reemplazar los códigos por el ID de la tabla
    df["academicProgramId"] = df["program_code"].map(program_lookup)

    # Filtrar filas donde no se encontró el ID
    df = df.dropna(subset=["academicProgramId"])

    # Convertir academicProgramId a entero (por si quedó como float por NaNs)
    df["academicProgramId"] = df["academicProgramId"].astype(int)

    # Eliminar duplicados si es necesario
    df = df.drop_duplicates(subset=["version", "academicProgramId"])


    # Insertar en la base de datos
    for _, row in df.iterrows():
        try:
            await database.pensum.create({
                "version": int(row["version"]),
                "academicProgramId": row["academicProgramId"]
            })
        except Exception as e:
            print(f"Error inserting row: {row} - {e}")
