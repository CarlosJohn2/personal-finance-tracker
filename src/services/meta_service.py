"""Serviço de regras de negócio para Metas financeiras."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.meta import Meta
from src.repositories.meta_repo import MetaRepository


class MetaService:
    """Orquestra regras de negócio para metas financeiras.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        self.repo = MetaRepository(sessao)

    def criar(
        self,
        nome: str,
        valor_alvo: Decimal,
        data_limite: Optional[date] = None,
        categoria_id: Optional[int] = None,
    ) -> Meta:
        """Cria uma nova meta financeira.

        Args:
            nome: Nome descritivo da meta.
            valor_alvo: Valor total a atingir.
            data_limite: Prazo para conclusão (opcional).
            categoria_id: Categoria associada (opcional).

        Returns:
            Meta: Meta criada.

        Raises:
            ValueError: Se valor_alvo for zero ou negativo.
        """
        if valor_alvo <= 0:
            raise ValueError("O valor alvo deve ser maior que zero.")
        return self.repo.criar(
            nome=nome.strip(),
            valor_alvo=valor_alvo,
            valor_atual=Decimal("0.00"),
            data_limite=data_limite,
            ativa=True,
            categoria_id=categoria_id,
        )

    def depositar(self, id: int, valor: Decimal) -> Meta:
        """Registra aporte na meta, incrementando o valor_atual.

        Args:
            id: ID da meta.
            valor: Valor a aportar (deve ser > 0).

        Returns:
            Meta: Meta com progresso atualizado.

        Raises:
            ValueError: Se a meta não existir ou valor for inválido.
        """
        meta = self.repo.obter(id)
        if not meta:
            raise ValueError(f"Meta ID {id} não encontrada.")
        if not meta.ativa:
            raise ValueError("Não é possível aportar em uma meta inativa.")
        if valor <= 0:
            raise ValueError("O valor do aporte deve ser maior que zero.")

        novo_valor = meta.valor_atual + valor
        return self.repo.atualizar(id, valor_atual=novo_valor)

    def encerrar(self, id: int) -> Meta:
        """Encerra uma meta, marcando-a como inativa.

        Args:
            id: ID da meta.

        Returns:
            Meta: Meta encerrada.

        Raises:
            ValueError: Se a meta não for encontrada.
        """
        meta = self.repo.atualizar(id, ativa=False)
        if not meta:
            raise ValueError(f"Meta ID {id} não encontrada.")
        return meta

    def listar_ativas(self) -> List[Meta]:
        """Lista metas ativas ordenadas por prazo.

        Returns:
            List[Meta]: Metas ativas.
        """
        return self.repo.listar_ativas()

    def listar_todas(self) -> List[Meta]:
        """Lista todas as metas, ativas e encerradas.

        Returns:
            List[Meta]: Todas as metas.
        """
        return self.repo.listar_todas()

    def verificar_alertas(self) -> List[str]:
        """Verifica metas com alertas (vencidas, próximas ou concluídas).

        Returns:
            List[str]: Lista de mensagens de alerta formatadas.
        """
        alertas: List[str] = []
        hoje = date.today()

        for meta in self.repo.listar_ativas():
            if meta.concluida:
                alertas.append(f"✅  Meta '{meta.nome}' atingida! Parabéns!")
            elif meta.data_limite:
                dias = (meta.data_limite - hoje).days
                if dias < 0:
                    alertas.append(
                        f"🚨  Meta '{meta.nome}' VENCIDA há {abs(dias)} dias "
                        f"({meta.percentual:.1f}% concluída)"
                    )
                elif dias == 0:
                    alertas.append(
                        f"⏰  Meta '{meta.nome}' vence HOJE! "
                        f"({meta.percentual:.1f}% concluída)"
                    )
                elif dias <= 7:
                    alertas.append(
                        f"🔔  Meta '{meta.nome}' vence em {dias} dias "
                        f"({meta.percentual:.1f}% concluída)"
                    )
                elif dias <= 30:
                    alertas.append(
                        f"📅  Meta '{meta.nome}' vence em {dias} dias "
                        f"({meta.percentual:.1f}% concluída)"
                    )

        return alertas

    def obter(self, id: int) -> Optional[Meta]:
        """Obtém uma meta pelo ID.

        Args:
            id: ID da meta.

        Returns:
            Optional[Meta]: Meta ou None.
        """
        return self.repo.obter(id)
