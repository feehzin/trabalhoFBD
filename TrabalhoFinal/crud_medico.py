from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Medico, MedicoCreate, MedicoUpdate
from db import get_db

router = APIRouter()

@router.post("/", response_model=Medico, status_code=status.HTTP_201_CREATED)
def criar_medico(medico: MedicoCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Medico (crm, nome, especialidade) VALUES (%s, %s, %s) RETURNING crm, nome, especialidade",
            (medico.crm, medico.nome, medico.especialidade)
        )
        new_medico_data = cursor.fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="CRM já cadastrado.")
        raise HTTPException(status_code=400, detail=f"Erro ao criar médico: {e}")
    finally:
        cursor.close()

    return Medico(crm=new_medico_data[0], nome=new_medico_data[1], especialidade=new_medico_data[2])

@router.get("/", response_model=List[Medico])
def listar_medicos(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT crm, nome, especialidade FROM Medico")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar médicos: {e}")
    finally:
        cursor.close()

    return [
        Medico(crm=r[0], nome=r[1], especialidade=r[2]) for r in rows
    ]

@router.get("/{crm}", response_model=Medico)
def get_medico(crm: str, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT crm, nome, especialidade FROM Medico WHERE crm=%s",
        (crm,)
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    return Medico(crm=row[0], nome=row[1], especialidade=row[2])

@router.patch("/{crm}", response_model=Medico)
def atualizar_medico(crm: str, medico_update: MedicoUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT crm, nome, especialidade FROM Medico WHERE crm=%s",
        (crm,)
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        raise HTTPException(status_code=404, detail="Médico não encontrado.")

    medico_existente = Medico(
        crm=row[0],
        nome=row[1],
        especialidade=row[2]
    )

    update_data = medico_update.dict(exclude_unset=True)

    medico_atualizado = medico_existente.copy(update=update_data)

    try:
        cursor.execute(
            "UPDATE Medico SET nome=%s WHERE crm=%s",
            (medico_atualizado.nome, crm)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar médico: {e}")
    finally:
        cursor.close()

    return Medico(crm=crm, nome=medico_atualizado.nome, especialidade=medico_existente.especialidade)

@router.delete("/{crm}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_medico(crm: str, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Medico WHERE crm=%s",
            (crm,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Médico não encontrado.")
        db.commit()
    except Exception as e:
        db.rollback()
        if "violates foreign key constraint" in str(e):
            raise HTTPException(status_code=409, detail="Não é possível deletar médico com consultas associadas.")
        raise HTTPException(status_code=400, detail=f"Erro ao deletar médico: {e}")
    finally:
        cursor.close()