import json
from src.database import database
import pandas as pd
from src.modules.pensum.services import get_pensum_by_version_and_program_id
import asyncio

async def get_all_subjects():
    return await database.subject.find_many()

async def get_subjects_by_pensum_id(pensum_id: int):
    return await database.subject.find_many(where={"pensumId": pensum_id})

async def get_subject_by_pensum_id_and_code(pensum_id: int, code: str):
    return await database.subject.find_first(where={"pensumId": pensum_id, "code": code})

async def get_subject_by_code(code: str):
    return await database.subject.find_first(where={"code": code})

async def create_pre_requirements(data):
    return await database.prerequirement.create(data=data)

def clean_code(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()

async def insert_subject_from_excel():
    # Carga el archivo Excel
    df = pd.read_excel(r"D:\Escritorio\2.PensumIngSistemas.xlsx", engine="openpyxl")

    # Renombra las columnas
    df = df.rename(columns={
        "NIVEL": "level",
        #FIELDS no está en el archivo actual
        "CODIGO": "code",
        "CREDITOS": "credits",
        "NROBLOQUES": "weeklyHours",
        "NROSEMANAS": "weeks",
        #Validable no está en el archivo actual
        "HABILITABLE": "enableable",
        "PREREQUISITOS": "preRequirements",
        "COREQUISITOS": "coRequirements",
        "NOMBRE": "name",
        #TYPE no está en el archivo actual
        "VERSION": "version",
        "PROGRAMA": "program"
    })

    # Simula un mapeo código -> ID (esto deberías consultarlo de la BD realmente)
    program_lookup = {
        504: 1,
        506: 2,
        552: 3
    }

    enableable_lookup = {
        "S": True,
        "N": False
    }

    # Reemplazar los códigos por el ID de la tabla
    df["program"] = df["program"].map(program_lookup)

    # Convertir academicProgramId a entero (por si quedó como float por NaNs)
    df["program"] = df["program"].astype(int)

    # Reemplazar los códigos por el ID de la tabla
    df["level"] = df["level"].astype(int)
    df["enableable"] = df["enableable"].map(enableable_lookup)
    df["code"] = df["code"].astype(str) 
    df["credits"] = df["credits"].astype(int) 
    df["weeklyHours"] = df["weeklyHours"].fillna(0).astype(int)
    df["weeks"] = df["weeks"].astype(int) 
    df["preRequirements"] = df["preRequirements"].apply(clean_code)
    df["coRequirements"] = df["coRequirements"].apply(clean_code)

    # Insertar los datos en la base de datos
    for _, row in df.iterrows():
        #separo los prerequisitos y los requisitos de creditos 

        pensum = await get_pensum_by_version_and_program_id(row["version"], row["program"])
        if pensum is None:
            print(f"No se encontró pensum para version={row['version']} y program={row['program']}")
            return
        
        prerequisitos = row["preRequirements"].split(" AND ")
        credits_prerequisitos = [x for x in prerequisitos if "CR:" in x]
        code_prerequisitos = [x for x in prerequisitos if "CR:" not in x]

        if await get_subject_by_pensum_id_and_code(pensum.id, row["code"]) is not None:
            for code in code_prerequisitos:
                if code is None or code == "":
                    continue
                else:
                    subject = await get_subject_by_pensum_id_and_code(pensum.id, row["code"])
                    await create_pre_requirements(
                        data={
                            "code": code,
                            "subject": {
                                "connect": {"id": subject.id} 
                            }
                        })
        else:
            await database.subject.create(
                data={
                    "level": row["level"],
                    "fields": json.dumps({"1": "no data"}),
                    "code": row["code"],
                    "credits": row["credits"],
                    "weeklyHours": row["weeklyHours"],
                    "weeks": row["weeks"],
                    "validable": False, #no más info
                    "enableable": row["enableable"],
                    "coRequirements": str(row["coRequirements"]),
                    "creditRequirements": credits_prerequisitos[0] if credits_prerequisitos else None,
                    "name": row["name"],
                    "pensum": {
                        "connect": {"id": pensum.id}  # Asegúrate de que 'pensum.id' sea válido
                    }
                }
        )
        