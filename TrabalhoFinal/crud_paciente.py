from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Paciente, PacienteCreate, PacienteUpdate, TelefonePaciente, TelefonePacienteCreate, PacienteResponse, SexoEnum, TipoTelefoneEnum
from db import get_db

router = APIRouter()

@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def criar_paciente(paciente_data: PacienteCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Paciente (nome, data_nascimento, sexo, email, cpf) VALUES (%s, %s, %s, %s, %s) RETURNING id_paciente",
            (paciente_data.nome, paciente_data.data_nascimento, paciente_data.sexo.value, paciente_data.email, paciente_data.cpf)
        )
        new_paciente_id = cursor.fetchone()[0]

  
        db.commit()
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e) and "cpf" in str(e).lower():
            raise HTTPException(status_code=409, detail="CPF já cadastrado.")
        raise HTTPException(status_code=400, detail=f"Erro ao criar paciente: {e}")
    finally:
        cursor.close()

    return obter_paciente(new_paciente_id, db)

@router.get("/", response_model=List[PacienteResponse])
def listar_pacientes(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_paciente, nome, data_nascimento, sexo, email, cpf FROM Paciente")
        rows = cursor.fetchall()

        pacientes_list = []
        for p_row in rows:
            paciente_obj = Paciente(
                id_paciente=p_row[0],
                nome=p_row[1],
                data_nascimento=p_row[2],
                sexo=SexoEnum(p_row[3]),
                email=p_row[4],
                cpf=p_row[5]
            )
            response = PacienteResponse(**paciente_obj.dict())

            cursor.execute(
                "SELECT numero, tipo FROM Telefone_Paciente WHERE id_paciente = %s",
                (paciente_obj.id_paciente,)
            )
            phone_rows = cursor.fetchall()
            response.telefones = [TelefonePaciente(id_paciente=paciente_obj.id_paciente, numero=r[0], tipo=TipoTelefoneEnum(r[1])) for r in phone_rows]
            pacientes_list.append(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar pacientes: {e}")
    finally:
        cursor.close()

    return pacientes_list

@router.get("/{id_paciente}", response_model=PacienteResponse)
def obter_paciente(id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_paciente, nome, data_nascimento, sexo, email, cpf FROM Paciente WHERE id_paciente=%s",
            (id_paciente,)
        )
        p_row = cursor.fetchone()
        if not p_row:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

        paciente_obj = Paciente(
            id_paciente=p_row[0],
            nome=p_row[1],
            data_nascimento=p_row[2],
            sexo=SexoEnum(p_row[3]),
            email=p_row[4],
            cpf=p_row[5]
        )
        response = PacienteResponse(**paciente_obj.dict())

        cursor.execute(
            "SELECT numero, tipo FROM Telefone_Paciente WHERE id_paciente = %s",
            (id_paciente,)
        )
        phone_rows = cursor.fetchall()
        response.telefones = [TelefonePaciente(id_paciente=id_paciente, numero=r[0], tipo=TipoTelefoneEnum(r[1])) for r in phone_rows]
    finally:
        cursor.close()
    return response

@router.patch("/{id_paciente}", response_model=PacienteResponse)
def atualizar_paciente(id_paciente: int, paciente_update: PacienteUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id_paciente, nome, data_nascimento, sexo, email, cpf FROM Paciente WHERE id_paciente=%s",
            (id_paciente,)
        )
        p_row = cursor.fetchone()
        if not p_row:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

        paciente_existente = Paciente(
            id_paciente=p_row[0],
            nome=p_row[1],
            data_nascimento=p_row[2],
            sexo=SexoEnum(p_row[3]),
            email=p_row[4],
            cpf=p_row[5]
        )

        update_data = paciente_update.dict(exclude_unset=True)

        if 'sexo' in update_data:
            update_data['sexo'] = update_data['sexo'].value

        paciente_atualizado = paciente_existente.copy(update=update_data)

        sql_update_paciente = """
            UPDATE Paciente SET
                nome=%s, sexo=%s, email=%s
            WHERE id_paciente=%s
        """
        cursor.execute(
            sql_update_paciente,
            (
                paciente_atualizado.nome,
                paciente_atualizado.sexo.value,
                paciente_atualizado.email,
                id_paciente
            )
        )

        if paciente_update.telefones is not None:
            cursor.execute("DELETE FROM Telefone_Paciente WHERE id_paciente = %s", (id_paciente,))
            if paciente_update.telefones:
                for tel in paciente_update.telefones:
                    cursor.execute(
                        "INSERT INTO Telefone_Paciente (id_paciente, numero, tipo) VALUES (%s, %s, %s)",
                        (id_paciente, tel.numero, tel.tipo.value)
                    )
        db.commit()
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e) and "cpf" in str(e).lower():
            raise HTTPException(status_code=409, detail="CPF já cadastrado.")
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar paciente: {e}")
    finally:
        cursor.close()

    return obter_paciente(id_paciente, db)

@router.delete("/{id_paciente}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_paciente(id_paciente: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Telefone_Paciente WHERE id_paciente=%s",
            (id_paciente,)
        )
        cursor.execute(
            "DELETE FROM Paciente WHERE id_paciente=%s",
            (id_paciente,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        db.commit()
    except Exception as e:
        db.rollback()
        if "violates foreign key constraint" in str(e):
            raise HTTPException(status_code=409, detail="Não é possível deletar paciente com agendamentos, consultas ou encaminhamentos associados. Remova as associações primeiro.")
        raise HTTPException(status_code=400, detail=f"Erro ao deletar paciente: {e}")
    finally:
        cursor.close()