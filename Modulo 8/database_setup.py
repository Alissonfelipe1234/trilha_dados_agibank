import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


load_dotenv()
DB_URL = os.getenv("STRING_DB")

engine = create_engine(DB_URL, echo=False) # echo=True para debug de SQL no terminal

class Base(DeclarativeBase):
    """Classe base para todos os modelos."""
    pass

class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )

class Categoria(Base):
    __tablename__ = "categorias"
    id: Mapped[int] = mapped_column(primary_key=True)
    genero: Mapped[str] = mapped_column(String(50), unique=True)

class Livro(Base, TimestampMixin):
    __tablename__ = "livros"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    autor: Mapped[str] = mapped_column(String(100))
    sinopse: Mapped[str] = mapped_column(String(500))
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    volume: Mapped[int] = mapped_column(default=1)
    preco: Mapped[float] = mapped_column()
    quantidade: Mapped[int] = mapped_column()
    id_categoria: Mapped[int] = mapped_column(ForeignKey("categorias.id"))

class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    senha: Mapped[str] = mapped_column(String(255)) # Espaço para hashes de senha

class Avaliacao(Base, TimestampMixin):
    __tablename__ = "avaliacoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_livro: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nota: Mapped[int] = mapped_column()
    comentario: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Regra: Nota deve ser entre 0 e 5
    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 5", name="check_nota_range"),
    )

class Venda(Base, TimestampMixin):
    __tablename__ = "vendas"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_livro: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    quantidade: Mapped[int] = mapped_column()

class Emprestimo(Base, TimestampMixin):
    __tablename__ = "emprestimos"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_livro: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    dt_devolucao_prevista: Mapped[datetime] = mapped_column(DateTime)
    devolvido: Mapped[bool] = mapped_column(default=False)

class Multa(Base, TimestampMixin):
    __tablename__ = "multas"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    valor: Mapped[float] = mapped_column()
    descricao: Mapped[str] = mapped_column(String(255))

def init_db():
    Base.metadata.create_all(engine)
    print("Estrutura do banco verificada/criada.")

if __name__ == "__main__":
    init_db()