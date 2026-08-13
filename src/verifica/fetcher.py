from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import tempfile
import logging
import json

from .config import settings

class Fetcher:
    def __init__(self, path, local: bool = False):
        """Inicializa uma nova instância da classe

        Args:
            path (_type_): Caminho do arquivo de respostas ou URL do exercício
            local (bool, optional): Indica se o arquivo de respostas é local. O padrão é False.
        """
        self.exercise = path
        self.local = local
        if not local:
            self.base_url = settings.get_config("url")
            self.remote_path = f"{self.exercise.strip()}/{settings.get_config('answers_file_name')}"
        self.logger = logging.getLogger(__name__)

    def __str__(self):
        """Representação em string da classe

        Returns:
            _type_: String representando a instância da classe
        """
        return f"Fetcher(path=\"{self.path}\", local={self.local})"

    def _build_url(self) -> str:
        """Constroi a URL completa para o arquivo de respostas.

        Returns:
            str: URL formatada
        """
        return f"{self.base_url}/{self.remote_path}"

    def fetch(self) -> str:
        """Baixa o arquivo de respostas e salva em uma pasta temporária

        Raises:
            RuntimeError: Se não for possível buscar o exercício

        Returns:
            str: O caminho do arquivo salvo
        """
        try:
            self.logger.info("Baixando arquivo de correção...")
            request = Request(self._build_url())

            request.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
            request.add_header("Pragma", "no-cache")
            request.add_header("Expires", "0")

            with urlopen(request) as response:
                content = response.read().decode("utf-8")
        except (HTTPError, URLError) as error:
            self.logger.error(f"Falha ao buscar o arquivo de correção '{self.exercise}': {error}")
            raise RuntimeError(f"Falha ao buscar o arquivo de correção '{self.exercise}'") from error

        self.file = tempfile.NamedTemporaryFile(mode='w+t', prefix='verifica-', suffix='.json', encoding='utf-8')
        self.file.write(content)

        return self.file.name

    def get_file(self) -> str:
        """Busca o arquivo de respostas no caminho salvo em self.exercise

        Raises:
            FileNotFoundError: Se o arquivo de respostas não for encontrado no caminho local
            RuntimeError: Se o método for chamado quando local=False

        Returns:
            str: Caminho do arquivo de respostas
        """
        if self.local:
            local_path = Path(self.exercise) / settings.get_config("answers_file_name")
            if not local_path.is_file():
                raise FileNotFoundError(f"O arquivo de respostas não foi encontrado em '{local_path}'")
            self.file = open(local_path, 'r', encoding='utf-8')
            return str(local_path)
        raise RuntimeError("O método só pode ser usado quando local=True")


    def get_content(self) -> str:
        """Lê o conteúdo do arquivo

        Raises:
            ValueError: O arquivo de correção não existe

        Returns:
            str: Conteúdo do arquivo
        """
        if not self.file:
            raise ValueError("o arquivo de correção não existe")

        self.file.seek(0)
        return self.file.read()

    def get_decoded_json(self):
        """Transforma o JSON do arqivo salvo em objeto python

        Raises:
            ValueError: O arquivo de correção não existe
            RuntimeError: Falha ao decodificar o arquivo de correção

        Returns:
            _type_: Objeto python representando o JSON do arquivo
        """
        if not self.file:
            raise ValueError("o arquivo de correção não existe")

        try:
            decoded = json.loads(self.get_content())
        except json.JSONDecodeError as error:
            self.logger.error(f"Falha ao decodificar o arquivo de correção '{self.exercise}': {error}")
            raise RuntimeError(f"Falha ao decodificar o arquivo de correção '{self.exercise}'") from error

        return decoded


    def cleanup(self):
        """Deleta o arquivo temporário criado para o arquivo de respostas, caso exista."""
        if self.file != None:
            self.file.close()