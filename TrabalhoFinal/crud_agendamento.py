from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models import Agendamento, AgendamentoCreate, AgendamentoUpdate, StatusAgendamento
from db import get_db

router = APIRouter()

@router.post("/", response_model=Agendamento, status_code=status.HTTP_201_CREATED)
def criar_agendamento(agendamento: AgendamentoCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Agendamento (id_agendamento, id_paciente, data, observacoes, status) VALUES (DEFAULT, %s, %s, %s, %s) RETURNING id_agendamento",
            (agendamento.id_paciente, agendamento.data, agendamento.observacoes, 'Marcada')
        )
        new_id_agendamento = cursor.fetchone()[0]
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar agendamento: {e}")
    finally:
        cursor.close()

    return Agendamento(
        id_agendamento=new_id_agendamento,
        id_paciente=agendamento.id_paciente,
        data=agendamento.data,
        observacoes=agendamento.observacoes,
        status=StatusAgendamento.MARCADA
    )

@router.get("/", response_model=List[Agendamento])
def listar_agendamentos(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_agendamento, id_paciente, data, observacoes, status FROM Agendamento")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agendamentos: {e}")
    finally:
        cursor.close()

    return [
        Agendamento(
            id_agendamento=r[0],
            id_paciente=r[1],
            data=r[2],
            observacoes=r[3],
            status=r[4]
        ) for r in rows
    ]

@router.get("/{id_agendamento}/{id_paciente}", response_model=Agendamento)
def get_agendamento(id_agendamento: int, id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id_agendamento, id_paciente, data, observacoes, status FROM Agendamento WHERE id_agendamento=%s AND id_paciente=%s",
        (id_agendamento, id_paciente)
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return Agendamento(
        id_agendamento=row[0],
        id_paciente=row[1],
        data=row[2],
        observacoes=row[3],
        status=row[4]
    )

@router.patch("/{id_agendamento}/{id_paciente}", response_model=Agendamento)
def atualizar_agendamento(id_agendamento: int, id_paciente: int, agendamento_update: AgendamentoUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id_agendamento, id_paciente, data, observacoes, status FROM Agendamento WHERE id_agendamento=%s AND id_paciente=%s",
        (id_agendamento, id_paciente)
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    agendamento_existente = Agendamento(
        id_agendamento=row[0],
        id_paciente=row[1],
        data=row[2],
        observacoes=row[3],
        status=row[4]
    )

    update_data = agendamento_update.dict(exclude_unset=True)
    agendamento_atualizado = agendamento_existente.copy(update=update_data)

    try:
        cursor.execute(
            "UPDATE Agendamento SET data=%s, observacoes=%s, status=%s WHERE id_agendamento=%s AND id_paciente=%s",
            (agendamento_atualizado.data, agendamento_atualizado.observacoes, agendamento_atualizado.status, id_agendamento, id_paciente)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar agendamento: {e}")
    finally:
        cursor.close()

    return agendamento_atualizado

@router.delete("/{id_agendamento}/{id_paciente}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_agendamento(id_agendamento: int, id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Agendamento WHERE id_agendamento=%s AND id_paciente=%s",
            (id_agendamento, id_paciente)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        db.commit()
    except Exception as e:
        db.rollback()
        if "violates foreign key constraint" in str(e):
             raise HTTPException(status_code=409, detail="Não é possível deletar agendamento com consultas ou remarcas associadas.")
        raise HTTPException(status_code=400, detail=f"Erro ao deletar agendamento: {e}")
    finally:
        cursor.close()