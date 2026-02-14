from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.ingestion import IngestionService

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    allowed_extensions = [".pdf", ".md"]
    filename = file.filename.lower() #type:ignore

    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos PDF e Markdown (.md) são permitidos."
        )

    service = IngestionService(db)

    try:
        resultado = await service.process_pdf(file)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro no processamento: {str(e)}")
