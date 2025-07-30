from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from crud_clinica import router as clinica_router
from crud_agendamento import router as agendamento_router
from crud_encaminhamento import router as encaminhamento_router
from crud_relatorios import router as relatorios_router
from crud_medico import router as medico_router
from crud_paciente import router as paciente_router
from crud_remarca import router as remarca_router

app = FastAPI(
  title="SpeedMED - Sistema Clínico",
  version="1.0.0",
  description="API para gerenciamento de agendamentos, consultas e encaminhamentos em um sistema clínico."
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
  clinica_router,
  prefix="/consultas",
  tags=["Consultas"]
)

app.include_router(
  agendamento_router,
  prefix="/agendamentos",
  tags=["Agendamentos"]
)

app.include_router(
  encaminhamento_router,
  prefix="/encaminhamentos",
  tags=["Encaminhamentos"]
)

app.include_router(
  relatorios_router,
  prefix="/relatorios",
  tags=["Relatórios"]
)

app.include_router(
  medico_router,
  prefix="/medicos",
  tags=["Médicos"]
)

app.include_router(
  paciente_router,
  prefix="/pacientes",
  tags=["Pacientes"]
)

app.include_router(
  remarca_router,
  prefix="/remarcas",
  tags=["Remarcas"]
)