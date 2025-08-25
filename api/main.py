from fastapi import FastAPI, HTTPException, status
from typing import List
from contextlib import asynccontextmanager
import database
import models

# Gerenciador de Ciclo de Vida (Lifespan)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ação executada na inicialização da API para criar a tabela."""
    print("Inicializando a API e criando a tabela no banco de dados...")
    database.init_db()
    yield

# Instância Principal da API

app = FastAPI(
    title="API de Agendas (Tabela Única)",
    description="API para gerenciar eventos das agendas de IA, Marketing e RH em uma tabela unificada.",
    version="1.1.0",
    lifespan=lifespan
)

# Endpoints CRUD

@app.post("/eventos", response_model=models.EventoInDB, status_code=status.HTTP_201_CREATED)
def create_evento_endpoint(evento: models.EventoCreate):
    """Cria um novo evento no banco de dados."""
    novo_evento = database.create_evento(evento.model_dump())
    return novo_evento

@app.get("/eventos", response_model=List[models.EventoInDB])
def get_all_eventos_endpoint():
    """Retorna todos os eventos cadastrados."""
    return database.get_all_eventos()

@app.get("/eventos/{evento_id}", response_model=models.EventoInDB)
def get_evento_by_id_endpoint(evento_id: int):
    """Busca um evento específico pelo seu ID."""
    evento = database.get_evento_by_id(evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado")
    return evento

@app.put("/eventos/{evento_id}", response_model=models.EventoInDB)
def update_evento_endpoint(evento_id: int, evento_update: models.EventoUpdate):
    """Atualiza um evento existente pelo seu ID."""
    updated_evento = database.update_evento(evento_id, evento_update.model_dump(exclude_unset=True))
    if not updated_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado para atualizar")
    return updated_evento

@app.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento_endpoint(evento_id: int):
    """Deleta um evento pelo seu ID."""
    deleted = database.delete_evento(evento_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado para deletar")
    return