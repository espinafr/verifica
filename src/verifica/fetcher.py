from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import tempfile
import logging
import json

from .config import settings

class Fetcher:
    def __init__(self, path, local: bool = False):
        self.exercise = path
        self.local = local
        if not local:
            self.base_url = settings.get_config("url")
            self.remote_path = f"{self.exercise.strip()}/{settings.get_config('answers_file_name')}"
        self.logger = logging.getLogger(__name__)

    def __str__(self):
        return f"Fetcher(url=\"{self._build_url()}\")"

    def _build_url(self):
        return f"{self.base_url}/{self.remote_path}"

    def fetch(self) -> str:
        """Baixa o arquivo de respostas e salva em uma pasta temporária

        :returns: O caminho do arquivo salvo
        :rtype: str
        :raises RuntimeError: Se não for possível buscar o exercício
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

    def get_file(self):
        if self.local:
            local_path = Path(self.exercise) / settings.get_config("answers_file_name")
            if not local_path.is_file():
                raise FileNotFoundError(f"O arquivo de respostas não foi encontrado em '{local_path}'")
            self.file = open(local_path, 'r', encoding='utf-8')
            return str(local_path)


    def get_content(self):
        if not self.file:
            raise ValueError("o arquivo de correção não existe")

        self.file.seek(0)
        return self.file.read()

    def get_decoded_json(self):
        if not self.file:
            raise ValueError("o arquivo de correção não existe")

        return json.loads(self.get_content())

    def cleanup(self):
        if self.file != None:
            self.file.close()