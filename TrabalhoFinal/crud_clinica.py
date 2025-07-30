from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models import Consulta, ConsultaCreate, ConsultaUpdate
from db import get_db

router = APIRouter()

@router.post("/", response_model=Consulta, status_code=status.HTTP_201_CREATED)
def criar_consulta(consulta: ConsultaCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Consulta (crm, id_agendamento, id_paciente, data_hora, diagnostico, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                consulta.crm,
                consulta.id_agendamento,
                consulta.id_paciente,
                consulta.data_hora,
                consulta.diagnostico,
                consulta.observacoes
            )
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar consulta: {e}")
    finally:
        cursor.close()

    return consulta

@router.get("/", response_model=List[Consulta])
def listar_consultas(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT crm, id_agendamento, id_paciente, data_hora, diagnostico, observacoes FROM Consulta"
        )
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar consultas: {e}")
    finally:
        cursor.close()

    return [
        Consulta(
            crm=r[0],
            id_agendamento=r[1],
            id_paciente=r[2],
            data_hora=r[3],
            diagnostico=r[4],
            observacoes=r[5]
        ) for r in rows
    ]

@router.get("/{crm}/{id_agendamento}/{id_paciente}", response_model=Consulta)
def get_consulta(crm: str, id_agendamento: int, id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT crm, id_agendamento, id_paciente, data_hora, diagnostico, observacoes FROM Consulta WHERE crm=%s AND id_agendamento=%s AND id_paciente=%s",
        (crm, id_agendamento, id_paciente)
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return Consulta(
        crm=row[0],
        id_agendamento=row[1],
        id_paciente=row[2],
        data_hora=row[3],
        diagnostico=row[4],
        observacoes=row[5]
    )

@router.patch("/{crm}/{id_agendamento}/{id_paciente}", response_model=Consulta)
def atualizar_consulta(crm: str, id_agendamento: int, id_paciente: int, consulta_update: ConsultaUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT crm, id_agendamento, id_paciente, data_hora, diagnostico, observacoes FROM Consulta WHERE crm=%s AND id_agendamento=%s AND id_paciente=%s",
        (crm, id_agendamento, id_paciente)
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    consulta_existente = Consulta(
        crm=row[0],
        id_agendamento=row[1],
        id_paciente=row[2],
        data_hora=row[3],
        diagnostico=row[4],
        observacoes=row[5]
    )

    update_data = consulta_update.dict(exclude_unset=True)
    consulta_atualizada = consulta_existente.copy(update=update_data)

    try:
        cursor.execute(
            """
            UPDATE Consulta
            SET diagnostico=%s, observacoes=%s
            WHERE crm=%s AND id_agendamento=%s AND id_paciente=%s
            """,
            (consulta_atualizada.diagnostico, consulta_atualizada.observacoes, crm, id_agendamento, id_paciente)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar consulta: {e}")
    finally:
        cursor.close()

    return consulta_atualizada

@router.delete("/{crm}/{id_agendamento}/{id_paciente}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_consulta(crm: str, id_agendamento: int, id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Consulta WHERE crm=%s AND id_agendamento=%s AND id_paciente=%s",
            (crm, id_agendamento, id_paciente)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Consulta não encontrada.")
        db.commit()
    except Exception as e:
        db.rollback()
        if "violates foreign key constraint" in str(e):
             raise HTTPException(status_code=409, detail="Não é possível deletar consulta com encaminhamentos associados. Remova as associações primeiro.")
        raise HTTPException(status_code=400, detail=f"Erro ao deletar consulta: {e}")
    finally:
        cursor.close()