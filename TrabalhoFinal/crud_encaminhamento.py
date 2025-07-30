from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import (
    Encaminhamento, EncaminhamentoCreate, EncaminhamentoUpdate,
    EncaminhamentoResponse, ExameInfo, AgendamentoInfo, TipoEncaminhamento
)
from db import get_db

router = APIRouter()

@router.post("/", response_model=EncaminhamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_encaminhamento(encaminhamento_data: EncaminhamentoCreate, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        if encaminhamento_data.tipo == TipoEncaminhamento.EXAME and not encaminhamento_data.exames_ids:
            raise HTTPException(status_code=400, detail="Para encaminhamento de Exame, 'exames_ids' é obrigatório.")
        if encaminhamento_data.tipo == TipoEncaminhamento.CONSULTA and (not encaminhamento_data.agendamento_novo_id or not encaminhamento_data.paciente_novo_id):
            raise HTTPException(status_code=400, detail="Para encaminhamento de Consulta, 'agendamento_novo_id' e 'paciente_novo_id' são obrigatórios.")
        if encaminhamento_data.tipo == TipoEncaminhamento.AMBOS:
            if not encaminhamento_data.exames_ids:
                raise HTTPException(status_code=400, detail="Para encaminhamento 'Ambos', 'exames_ids' é obrigatório.")
            if not encaminhamento_data.agendamento_novo_id or not encaminhamento_data.paciente_novo_id:
                raise HTTPException(status_code=400, detail="Para encaminhamento 'Ambos', 'agendamento_novo_id' e 'paciente_novo_id' são obrigatórios.")


        sql_enc = """
            INSERT INTO Encaminhamento (id_agendamento, id_paciente, tipo, observacoes)
            VALUES (%s, %s, %s, %s) RETURNING id_encaminhamento
        """
        cursor.execute(sql_enc, (
            encaminhamento_data.id_agendamento,
            encaminhamento_data.id_paciente,
            encaminhamento_data.tipo.value,
            encaminhamento_data.observacoes
        ))
        new_enc_id = cursor.fetchone()[0]

        if encaminhamento_data.tipo == TipoEncaminhamento.EXAME or encaminhamento_data.tipo == TipoEncaminhamento.AMBOS:
            if encaminhamento_data.exames_ids:
                for exame_id in encaminhamento_data.exames_ids:
                    cursor.execute(
                        "INSERT INTO Encaminhamento_Exame (id_encaminhamento, id_exame) VALUES (%s, %s)",
                        (new_enc_id, exame_id)
                    )
        if encaminhamento_data.tipo == TipoEncaminhamento.CONSULTA or encaminhamento_data.tipo == TipoEncaminhamento.AMBOS:
            if encaminhamento_data.agendamento_novo_id and encaminhamento_data.paciente_novo_id:
                cursor.execute(
                    "INSERT INTO Encaminhamento_Consulta (id_encaminhamento, id_agendamento, id_paciente) VALUES (%s, %s, %s)",
                    (new_enc_id, encaminhamento_data.agendamento_novo_id, encaminhamento_data.paciente_novo_id)
                )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar encaminhamento: {e}")
    finally:
        cursor.close()

    return obter_encaminhamento(new_enc_id, db)

@router.get("/{id_encaminhamento}", response_model=EncaminhamentoResponse)
def obter_encaminhamento(id_encaminhamento: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_encaminhamento, id_agendamento, id_paciente, tipo, observacoes FROM Encaminhamento WHERE id_encaminhamento = %s", (id_encaminhamento,))
        enc_base = cursor.fetchone()
        if not enc_base:
            raise HTTPException(status_code=404, detail="Encaminhamento não encontrado.")

        enc_obj = Encaminhamento(
            id_encaminhamento=enc_base[0],
            id_agendamento=enc_base[1],
            id_paciente=enc_base[2],
            tipo=enc_base[3],
            observacoes=enc_base[4]
        )
        response = EncaminhamentoResponse(**enc_obj.dict())

        if enc_obj.tipo == TipoEncaminhamento.EXAME or enc_obj.tipo == TipoEncaminhamento.AMBOS:
            cursor.execute("""
                SELECT e.id_exame, e.nome FROM Exame e
                JOIN Encaminhamento_Exame ee ON e.id_exame = ee.id_exame
                WHERE ee.id_encaminhamento = %s
            """, (id_encaminhamento,))
            response.exames = [ExameInfo(id_exame=r[0], nome=r[1]) for r in cursor.fetchall()]

        if enc_obj.tipo == TipoEncaminhamento.CONSULTA or enc_obj.tipo == TipoEncaminhamento.AMBOS:
            cursor.execute("""
                SELECT a.id_agendamento, a.id_paciente, a.data FROM Agendamento a
                JOIN Encaminhamento_Consulta ec ON a.id_agendamento = ec.id_agendamento AND a.id_paciente = ec.id_paciente
                WHERE ec.id_encaminhamento = %s
            """, (id_encaminhamento,))
            row = cursor.fetchone()
            if row:
                response.consulta_agendada = AgendamentoInfo(id_agendamento=row[0], id_paciente=row[1], data=row[2])
    finally:
        cursor.close()
    return response