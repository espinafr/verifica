import logging 

logger = logging.getLogger(__name__)

class Result:
    """Classe responsável por armazenar o resultado de um teste"""

    def __init__(self, success: bool, error: str = "") -> None:
        """Atribui os parâmetros passados para o objeto

        Args:
            success (bool): Resultado do teste
            error (str): Mensagem de erro, se houver
        """
        self.success = success
        self.error = error


    def __str__(self) -> str:
        """Retorna uma representação em string do resultado

        Returns:
            str: Representação em string do resultado
        """
        return f"Result(success={self.success}, error='{self.error}')"
