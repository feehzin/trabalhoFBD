from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Remarca, RemarcaCreate
from db import get_db

router = APIRouter()

@router.post("/", response_model=Remarca, status_code=status.HTTP_201_CREATED)
def criar_remarca(remarca_data: RemarcaCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Remarca (antigo_id_agendamento, antigo_id_paciente,
                                 novo_id_agendamento, novo_id_paciente,
                                 motivo, data_remarcacao, quem_solicitou)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_remarca, antigo_id_agendamento, antigo_id_paciente, novo_id_agendamento, novo_id_paciente, motivo, data_remarcacao, quem_solicitou
            """,
            (
                remarca_data.antigo_id_agendamento,
                remarca_data.antigo_id_paciente,
                remarca_data.novo_id_agendamento,
                remarca_data.novo_id_paciente,
                remarca_data.motivo,
                remarca_data.data_remarcacao,
                remarca_data.quem_solicitou
            )
        )
        new_remarca_data = cursor.fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar remarca: {e}")
    finally:
        cursor.close()

    return Remarca(
        id_remarca=new_remarca_data[0],
        antigo_id_agendamento=new_remarca_data[1],
        antigo_id_paciente=new_remarca_data[2],
        novo_id_agendamento=new_remarca_data[3],
        novo_id_paciente=new_remarca_data[4],
        motivo=new_remarca_data[5],
        data_remarcacao=new_remarca_data[6],
        quem_solicitou=new_remarca_data[7]
    )

@router.get("/", response_model=List[Remarca])
def listar_remarcas(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_remarca, antigo_id_agendamento, antigo_id_paciente, novo_id_agendamento, novo_id_paciente, motivo, data_remarcacao, quem_solicitou FROM Remarca"
        )
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar remarcas: {e}")
    finally:
        cursor.close()

    return [
        Remarca(
            id_remarca=r[0],
            antigo_id_agendamento=r[1],
            antigo_id_paciente=r[2],
            novo_id_agendamento=r[3],
            novo_id_paciente=r[4],
            motivo=r[5],
            data_remarcacao=r[6],
            quem_solicitou=r[7]
        ) for r in rows
    ]