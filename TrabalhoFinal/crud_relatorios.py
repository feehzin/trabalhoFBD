from fastapi import APIRouter, Depends, HTTPException
from typing import List
from db import get_db
from models import (
    AgendamentoStatusReport, MedicoTotalConsultasReport, EncaminhamentoTipoReport,
    PacienteCardiologiaReport, CategoriaPacienteReport, UltimoAgendamentoPacienteReport,
    ConsultasEncaminhamentosReport, ExamesConsultasPacienteReport
)

router = APIRouter()

@router.get("/agendamentos-por-status", response_model=List[AgendamentoStatusReport], summary="Número de agendamentos por status")
def get_agendamentos_por_status(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("REFRESH MATERIALIZED VIEW categoria_paciente") 
        cursor.execute("REFRESH MATERIALIZED VIEW ultimo_agendamento_paciente")
        cursor.execute("REFRESH MATERIALIZED VIEW consultas_encaminhamentos")
        cursor.execute("REFRESH MATERIALIZED VIEW exames_consultas_por_paciente")
        db.commit() 

        cursor.execute("SELECT status, COUNT(*) AS total FROM Agendamento GROUP BY status")
        rows = cursor.fetchall()
        return [AgendamentoStatusReport(status=r[0], total=r[1]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter agendamentos por status: {e}")
    finally:
        cursor.close()

@router.get("/medicos-total-consultas", response_model=List[MedicoTotalConsultasReport], summary="Médicos que realizaram consultas, com contagem")
def get_medicos_total_consultas(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT
                m.nome AS medico,
                COUNT(*) AS total_consultas
            FROM Consulta c
            JOIN Medico m ON c.crm = m.crm
            GROUP BY m.nome
            ORDER BY total_consultas DESC
        """)
        rows = cursor.fetchall()
        return [MedicoTotalConsultasReport(medico=r[0], total_consultas=r[1]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter médicos e total de consultas: {e}")
    finally:
        cursor.close()

@router.get("/encaminhamentos-por-tipo", response_model=List[EncaminhamentoTipoReport], summary="Quantidade de encaminhamentos por tipo")
def get_encaminhamentos_por_tipo(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT tipo, COUNT(*) AS quantidade FROM Encaminhamento GROUP BY tipo")
        rows = cursor.fetchall()
        return [EncaminhamentoTipoReport(tipo=r[0], quantidade=r[1]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter encaminhamentos por tipo: {e}")
    finally:
        cursor.close()

@router.get("/pacientes-cardiologia", response_model=List[PacienteCardiologiaReport], summary="Pacientes que fizeram consultas com médicos da especialidade 'Cardiologia'")
def get_pacientes_cardiologia(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT
                p.nome AS paciente,
                m.nome AS medico,
                m.especialidade
            FROM Consulta c
            JOIN Medico m ON c.crm = m.crm
            JOIN Agendamento a ON c.id_agendamento = a.id_agendamento AND c.id_paciente = a.id_paciente
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            WHERE m.especialidade = 'Cardiologia'
        """)
        rows = cursor.fetchall()
        return [PacienteCardiologiaReport(paciente=r[0], medico=r[1], especialidade=r[2]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter pacientes da cardiologia: {e}")
    finally:
        cursor.close()

@router.get("/categoria-paciente", response_model=List[CategoriaPacienteReport], summary="Visão de categorização de pacientes por frequência de agendamentos")
def get_categoria_paciente(db=Depends(get_db)):
    cursor = db.cursor()
    try:

        cursor.execute("SELECT nome, total_agendamentos, categoria FROM categoria_paciente")
        rows = cursor.fetchall()
        return [CategoriaPacienteReport(nome=r[0], total_agendamentos=r[1], categoria=r[2]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter categoria de paciente: {e}")
    finally:
        cursor.close()

@router.get("/ultimo-agendamento-paciente", response_model=List[UltimoAgendamentoPacienteReport], summary="Visão do último agendamento e contato do paciente")
def get_ultimo_agendamento_paciente(db=Depends(get_db)):
    cursor = db.cursor()
    try:

        cursor.execute("SELECT nome, telefone_paciente, tipo_telefone, status FROM ultimo_agendamento_paciente")
        rows = cursor.fetchall()
        return [UltimoAgendamentoPacienteReport(nome=r[0], telefone_paciente=r[1], tipo_telefone=r[2], status=r[3]) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter último agendamento por paciente: {e}")
    finally:
        cursor.close()

@router.get("/consultas-encaminhamentos", response_model=List[ConsultasEncaminhamentosReport], summary="Visão de consultas e tipos de encaminhamentos gerados")
def get_consultas_encaminhamentos(db=Depends(get_db)):
    cursor = db.cursor()
    try:

        cursor.execute("SELECT nome_medico, especialidade, nome_paciente, diagnostico, data_consulta, tipo_encaminhamento FROM consultas_encaminhamentos")
        rows = cursor.fetchall()
        return [ConsultasEncaminhamentosReport(
            nome_medico=r[0],
            especialidade=r[1],
            nome_paciente=r[2],
            diagnostico=r[3],
            data_consulta=r[4],
            tipo_encaminhamento=r[5]
        ) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter consultas e encaminhamentos: {e}")
    finally:
        cursor.close()

@router.get("/exames-consultas-por-paciente", response_model=List[ExamesConsultasPacienteReport], summary="Visão de exames e consultas por paciente")
def get_exames_consultas_por_paciente(db=Depends(get_db)):
    cursor = db.cursor()
    try:
        
        cursor.execute("SELECT nome_paciente, count, exames_realizados, total_consultas FROM exames_consultas_por_paciente")
        rows = cursor.fetchall()
        return [ExamesConsultasPacienteReport(
            nome_paciente=r[0],
            count=r[1],
            exames_realizados=r[2],
            total_consultas=r[3]
        ) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter exames e consultas por paciente: {e}")
    finally:
        cursor.close()