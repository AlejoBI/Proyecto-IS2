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

def test_save_document_file_not_found(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Crear el mock de UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"

    # Simular el contenido del archivo
    mock_file.file = MagicMock()
    mock_file.file.read.return_value = b"Test file content"

    # Simular FileReader devolviendo un mensaje de error "File not found"
    FileReader.read_file = MagicMock(return_value="File not found: test_document.txt")

    result = rag_service.save_document(mock_file)

    # Comprobar que se devuelve el mensaje de error esperado
    assert result == {"status": "File not found: test_document.txt"}
    mongo_repo.save_document.assert_not_called()
    document_repo.save_document.assert_not_called()

def test_save_document_value_error(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Crear el mock de UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"

    # Simular el contenido del archivo
    mock_file.file = MagicMock()
    mock_file.file.read.return_value = b"Test file content"

    # Simular FileReader arrojando un ValueError
    FileReader.read_file = MagicMock(side_effect=ValueError("Unsupported file format"))

    result = rag_service.save_document(mock_file)

    # Comprobar que se devuelve el mensaje de error esperado
    assert result == {"status": "Unsupported file format"}
    mongo_repo.save_document.assert_not_called()
    document_repo.save_document.assert_not_called()

def test_save_document_generic_exception(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Crear el mock de UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"

    # Simular el contenido del archivo
    mock_file.file = MagicMock()
    mock_file.file.read.return_value = b"Test file content"

    # Simular FileReader arrojando una excepción genérica
    FileReader.read_file = MagicMock(side_effect=Exception("Something went wrong"))

    result = rag_service.save_document(mock_file)

    # Comprobar que se devuelve el mensaje de error esperado
    assert result == {"status": "Something went wrong"}
    mongo_repo.save_document.assert_not_called()
    document_repo.save_document.assert_not_called()


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

def test_get_user_not_found(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    email = "nonexistent@example.com"
    password = "password"

    # Simular que el método get_user del repositorio devuelve None (usuario no encontrado)
    mongo_repo.get_user.return_value = None

    result = rag_service.get_user(email, password)

    # Comprobar que el resultado es None cuando no se encuentra el usuario
    assert result is None
    mongo_repo.get_user.assert_called_once_with(email, password)

def test_get_user_exception(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    email = "test@example.com"
    password = "password"

    # Simular que el método get_user del repositorio lanza una excepción
    mongo_repo.get_user.side_effect = Exception("Database error")

    result = rag_service.get_user(email, password)

    # Comprobar que el resultado es None cuando ocurre una excepción
    assert result is None
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

def test_save_user_exception(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Añadir el campo 'role' que es requerido por el modelo User
    user = User(email="test@example.com", password="password", username="test_user", role="user")

    # Simular que el método save_user del repositorio lanza una excepción
    mongo_repo.save_user.side_effect = Exception("Database error")

    result = rag_service.save_user(user)

    # Comprobar que el resultado es None cuando ocurre una excepción
    assert result is None
    mongo_repo.save_user.assert_called_once_with(user)


# Pruebas unitarias para el método get_document
def test_get_document_success(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Configurar el documento de prueba
    mock_document = Document(id="123", title="Test Doc", content="Test content")
    mongo_repo.get_document.return_value = mock_document

    # Llamar al método get_document
    result = rag_service.get_document("123")

    # Verificar que se llama al repositorio y se obtiene el documento correcto
    mongo_repo.get_document.assert_called_once_with("123")
    assert result == mock_document


def test_get_document_not_found(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Simular que el documento no existe
    mongo_repo.get_document.return_value = None

    # Llamar al método get_document
    result = rag_service.get_document("123")

    # Verificar que no se encuentra el documento
    mongo_repo.get_document.assert_called_once_with("123")
    assert result is None


# Pruebas unitarias para el método get_vectors
def test_get_vectors_success(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Configurar la lista de vectores de prueba
    mock_vectors = ["vector1", "vector2", "vector3"]
    document_repo.get_vectors.return_value = mock_vectors

    # Llamar al método get_vectors
    result = rag_service.get_vectors()

    # Verificar que se llama al repositorio y se obtienen los vectores
    document_repo.get_vectors.assert_called_once()
    assert result == mock_vectors


def test_get_vectors_empty(rag_service, mock_repositories):
    document_repo, mongo_repo, openai_adapter = mock_repositories

    # Simular que no hay vectores
    document_repo.get_vectors.return_value = []

    # Llamar al método get_vectors
    result = rag_service.get_vectors()

    # Verificar que se devuelve una lista vacía
    document_repo.get_vectors.assert_called_once()
    assert result == []
