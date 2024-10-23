import pytest
from unittest.mock import MagicMock
from server.core.models import Document, User
from server.core import ports
from server.helpers.strategies import FileReader
from fastapi import UploadFile
from datetime import timedelta
import bcrypt
import os
from server.middlewares.jwt import create_access_token
from server.app.usecases import RAGService


@pytest.fixture
def mock_repositories():
    document_repo = MagicMock(spec=ports.DocumentRepositoryPort)
    mongo_repo = MagicMock(spec=ports.MongoDBRepositoryPort)
    openai_adapter = MagicMock(spec=ports.LlmPort)
    return document_repo, mongo_repo, openai_adapter


@pytest.fixture
def rag_service(mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories
    return RAGService(document_repo, mongo_repo, openai_adapter)


# Prueba de E2E: subir un documento, hacer una pregunta y obtener una respuesta
def test_chat_rag_e2e(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Simulación de la subida de un documento
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"
    mock_file.file = MagicMock()  # Crear un mock para el atributo 'file'
    mock_file.file.read.return_value = b"Este es un documento de prueba"

    # Simular FileReader para leer el contenido del documento
    FileReader.read_file = MagicMock(return_value="Este es el contenido del documento de prueba.")

    # Simular la subida del documento
    result = rag_service.save_document(mock_file)
    assert result == {"status": "Document saved successfully"}

    # Asegurarse que los repositorios interactúan correctamente
    mongo_repo.save_document.assert_called_once()
    document_repo.save_document.assert_called_once()

    # Simular la generación de respuesta de OpenAI
    query = "¿Qué dice el documento?"
    document_repo.get_documents.return_value = [
        Document(title="test_document.txt", content="Este es el contenido del documento de prueba.")]
    openai_adapter.generate_text.return_value = "Este es el contenido del documento."

    # Hacer la pregunta al RAGService
    response = rag_service.generate_answer(query)

    # Verificar que OpenAI fue llamado correctamente y que la respuesta es la esperada
    document_repo.get_documents.assert_called_once_with(query, openai_adapter)
    openai_adapter.generate_text.assert_called_once_with(prompt=query,
                                                         retrieval_context="Este es el contenido del documento de prueba.")

    assert response == "Este es el contenido del documento."


# Prueba unitaria para generar una respuesta
def test_generate_answer(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories
    document_repo.get_documents.return_value = [Document(title="Test Doc", content="This is the content")]

    openai_adapter.generate_text.return_value = "Generated answer"

    query = "What is AI?"
    result = rag_service.generate_answer(query)

    document_repo.get_documents.assert_called_once_with(query, openai_adapter)
    openai_adapter.generate_text.assert_called_once_with(prompt=query, retrieval_context="This is the content")

    assert result == "Generated answer"


# Prueba unitaria para guardar un documento
def test_save_document(rag_service, mock_repositories, tmpdir):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Crear el mock de UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"

    # Simular el contenido del archivo
    mock_file.file = MagicMock()  # Crear un mock para el atributo 'file'
    mock_file.file.read.return_value = b"Test file content"  # Simular la lectura del archivo

    # Mock de la función que guarda el archivo en la carpeta media
    tmpdir_path = tmpdir.mkdir("media")
    file_path = os.path.join(tmpdir_path, "test_document.txt")

    # Simular FileReader para leer el contenido
    FileReader.read_file = MagicMock(return_value="Test file content")

    result = rag_service.save_document(mock_file)

    assert result == {"status": "Document saved successfully"}
    mongo_repo.save_document.assert_called_once()
    document_repo.save_document.assert_called_once()


# Prueba unitaria para obtener un usuario correctamente
def test_get_user_success(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    email = "test@example.com"
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    mongo_repo.get_user.return_value = {
        "email": email,
        "username": "test_user",
        "password": hashed_password
    }

    result = rag_service.get_user(email, password)

    assert result["email"] == email
    assert result["username"] == "test_user"
    mongo_repo.get_user.assert_called_once_with(email, password)


# Prueba unitaria para guardar un usuario
def test_save_user(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Añadir el campo 'role' que es requerido por el modelo User
    user = User(email="test@example.com", password="password", username="test_user", role="user")

    mongo_repo.save_user.return_value = {"status": "success"}

    result = rag_service.save_user(user)

    assert result["status"] == "success"
    mongo_repo.save_user.assert_called_once_with(user)
