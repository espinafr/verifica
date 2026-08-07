from pathlib import Path

class Checker:
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Checa se um arquivo existe em determinado caminho

        :param file_path: Caminho do arquivo
        :returns: Verdadeiro caso exista
        :rtype: bool
        """
        return Path(file_path)

    def __init__(self, exercises_path: str, answers: dict):
        """Atribui os parâmetros passados para o objeto
        
        :param exercises_path: Caminho da pasta com arquivos do exercício
        :param answers: Dicionário de respostas no formato apropriado
        """
        self.exercises_path = exercises_path
        self.answers = answers
        self.roadmap = []

    def setup_roadmap(self) -> None:
        """Cria a lista de características do programa a serem testadas e salva em self"""
        # Arquivos existem?
        for file in self.answers.files:
            self.roadmap.append({
                "info": "existe",
                "args": file,
                "action": self.file_exists
            })

        # Todas as checagens de cada arquivo
        for file in self.answers.files:
            pass

        



    def test_CLI(self):
        pass

    def test_CLASS(self):
        pass

    def test_FUNCTION(self):
        pass

    def test_INPUT(self):
        pass

    def test_SEQUENCE_INPUT(self):
        pass