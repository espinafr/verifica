from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from config import settings

class Fetcher:
    def __init__(self, path):
        self.exercise = self._normalize_path(path)
        self.base_url = settings.get_config("url")
        self.remote_path = f"{self.exercise}/atv.json"
        self._tempdir = None

    @staticmethod
    def _normalize_path(path):
        exercise = Path(str(path).strip()).name.strip("/")
        if not exercise:
            raise ValueError("o caminho do exercício não pode ser vazio")
        return exercise

    def _build_url(self):
        return f"{self.base_url}/{self.remote_path}"

    def fetch(self, destination=None):
        try:
            with urlopen(self._build_url()) as response:
                content = response.read().decode("utf-8")
        except (HTTPError, URLError) as error:
            raise RuntimeError(f"falha ao buscar o exercício '{self.exercise}'") from error

        if destination is None:
            self._tempdir = TemporaryDirectory(prefix=f"verifica-{self.exercise}-")
            destination = Path(self._tempdir.name)
        else:
            destination = Path(destination)

        exercise_dir = destination / self.exercise
        exercise_dir.mkdir(parents=True, exist_ok=True)

        init_file = exercise_dir / "__init__.py"
        init_file.write_text(content, encoding="utf-8")
        return exercise_dir

    def cleanup(self):
        if self._tempdir is not None:
            self._tempdir.cleanup()
            self._tempdir = None