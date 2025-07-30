from pydantic import BaseModel
from typing import List, Optional 
from datetime import date, datetime
from enum import Enum

class StatusAgendamento(str, Enum):
    MARCADA = 'Marcada'
    AUSENTE = 'Ausente'
    CANCELADA = 'Cancelada'
    REALIZADA = 'Realizada'
    REMARCADA = 'Remarcada'

class TipoEncaminhamento(str, Enum):
    EXAME = 'Exame'
    CONSULTA = 'Consulta'
    AMBOS = 'Ambos'

class SexoEnum(str, Enum):
    FEMININO = 'F'
    MASCULINO = 'M'
    OUTRO = 'O'

class TipoTelefoneEnum(str, Enum):
    CELULAR = 'Celular'
    RESIDENCIAL = 'Residencial'


class Paciente(BaseModel):
    id_paciente: int
    nome: str
    data_nascimento: date
    sexo: SexoEnum
    email: Optional[str] = None 
    cpf: str 

class TelefonePaciente(BaseModel):
    id_paciente: int
    numero: str
    tipo: TipoTelefoneEnum

class Medico(BaseModel):
    crm: str
    nome: str
    especialidade: str

class Agendamento(BaseModel):
    id_agendamento: int
    id_paciente: int
    data: datetime
    observacoes: Optional[str] = None
    status: StatusAgendamento

class Consulta(BaseModel):
    crm: str
    id_agendamento: int
    id_paciente: int
    data_hora: datetime
    diagnostico: str
    observacoes: Optional[str] = None

class Remarca(BaseModel):
    id_remarca: int
    antigo_id_agendamento: int
    antigo_id_paciente: int
    novo_id_agendamento: int
    novo_id_paciente: int
    motivo: Optional[str] = None
    data_remarcacao: date
    quem_solicitou: Optional[str] = None

class Encaminhamento(BaseModel):
    id_encaminhamento: int
    id_agendamento: int
    id_paciente: int
    tipo: TipoEncaminhamento
    observacoes: Optional[str] = None

class Exame(BaseModel):
    id_exame: int
    nome: str
    descricao: Optional[str] = None

class EncaminhamentoExame(BaseModel):
    id_encaminhamento: int
    id_exame: int

class EncaminhamentoConsulta(BaseModel):
    id_encaminhamento: int
    id_agendamento: int
    id_paciente: int

# --- Modelos para operações CRUD (Create, Update) ---

# Consulta Create e Update (sem alteração)
class ConsultaCreate(BaseModel):
    crm: str
    id_agendamento: int
    id_paciente: int
    data_hora: datetime
    diagnostico: str
    observacoes: Optional[str] = None

class ConsultaUpdate(BaseModel):
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None

# Agendamento Create e Update (sem alteração)
class AgendamentoCreate(BaseModel):
    id_paciente: int
    data: datetime
    observacoes: Optional[str] = None

class AgendamentoUpdate(BaseModel):
    id_paciente: Optional[int] = None
    data: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: Optional[StatusAgendamento] = None


class EncaminhamentoCreate(BaseModel):
    id_agendamento: int
    id_paciente: int
    tipo: TipoEncaminhamento
    observacoes: Optional[str] = None
    exames_ids: Optional[List[int]] = None
    agendamento_novo_id: Optional[int] = None
    paciente_novo_id: Optional[int] = None

class EncaminhamentoUpdate(BaseModel):
    observacoes: Optional[str] = None


class MedicoCreate(BaseModel):
    crm: str
    nome: str
    especialidade: str

class MedicoUpdate(BaseModel):
    nome: Optional[str] = None


class TelefonePacienteCreate(BaseModel):
    numero: str
    tipo: TipoTelefoneEnum

class PacienteCreate(BaseModel):
    nome: str
    data_nascimento: date
    sexo: SexoEnum
    email: Optional[str] = None
    cpf: str

class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    sexo: Optional[SexoEnum] = None
    email: Optional[str] = None
    telefones: Optional[List[TelefonePacienteCreate]] = None

class RemarcaCreate(BaseModel):
    antigo_id_agendamento: int
    antigo_id_paciente: int
    novo_id_agendamento: int
    novo_id_paciente: int
    motivo: Optional[str] = None
    data_remarcacao: date
    quem_solicitou: Optional[str] = None

class ExameInfo(BaseModel):
    id_exame: int
    nome: str

class AgendamentoInfo(BaseModel):
    id_agendamento: int
    id_paciente: int
    data: datetime

class EncaminhamentoResponse(Encaminhamento):
    exames: List[ExameInfo] = []
    consulta_agendada: Optional[AgendamentoInfo] = None

class PacienteResponse(Paciente):
    telefones: List[TelefonePaciente] = []

class AgendamentoStatusReport(BaseModel):
    status: str
    total: int

class MedicoTotalConsultasReport(BaseModel):
    medico: str
    total_consultas: int

class EncaminhamentoTipoReport(BaseModel):
    tipo: str
    quantidade: int

class PacienteCardiologiaReport(BaseModel):
    paciente: str
    medico: str
    especialidade: str

class CategoriaPacienteReport(BaseModel):
    nome: str
    total_agendamentos: int
    categoria: str

class UltimoAgendamentoPacienteReport(BaseModel):
    nome: str
    telefone_paciente: str
    tipo_telefone: str
    status: str

class ConsultasEncaminhamentosReport(BaseModel):
    nome_medico: str
    especialidade: str
    nome_paciente: str
    diagnostico: str
    data_consulta: datetime
    tipo_encaminhamento: str

class ExamesConsultasPacienteReport(BaseModel):
    nome_paciente: str
    count: int
    exames_realizados: str
    total_consultas: int