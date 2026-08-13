from colorama import Fore, Style
from pathlib import Path
import traceback
from types import SimpleNamespace

from .shared import Result, logger
from .cli import test_CLI
from .inputs import test_INPUTS
from .imported import ClassTester, FunctionTester, Imported

class Checker:
    """Classe responsável por validar exercícios baseado em um arquivo de correção"""

    def __init__(self, exercises_path: str, answers: dict) -> None:
        """Atribui os parâmetros passados para a classe e inicializa a lista de roadmap

        Args:
            exercises_path (str): Caminho da pasta com arquivos do exercício
            answers (dict): Dicionário de respostas no formato apropriado
        """
        self.exercises_path = exercises_path
        self.answers = answers
        self.roadmap = []

    
    def __file_exists(self, file_path: str) -> bool:
        """Checa se um arquivo existe em determinado caminho

        Args:
            file_path (str): Caminho do arquivo

        Returns:
            bool: Booleano indicando se o arquivo existe
        """
        exists = Path(self.exercises_path / file_path).is_file()
        return Result(exists, "" if exists else f"Arquivo '{file_path}' não encontrado")


    def setup_roadmap(self) -> bool:
        """Popula a lista roadmap com uma sequência de testes a serem realizados

        Raises:
            ValueError: Arquivo de correção não possui características a serem testadas
            ValueError: Característica desconhecida no arquivo de correção

        Returns:
            bool: Booleano indicando se o roadmap foi configurado com sucesso
        """
        try:
            logger.info(f"Configurando roadmap")
            for file in self.answers["files"]:
                current_file_path = Path(self.exercises_path) / file
                logger.info(f"Inicindo detecções para o arquivo '{file}'")

                if len(self.answers[file]) == 0:
                    raise ValueError(f"O arquivo de correção para '{file}' não possui características a serem testadas")

                logger.info(file)
                self.roadmap.append({
                    "info": f"'{file}' existe",
                    "args": [self, file],
                    "action": Checker.__file_exists
                })

                for check_step, subsequent_steps in self.answers[file].items():
                    logger.info(f"CARACTERÍSTICA DETECTADA: {check_step}")
                    if check_step == "CLI":
                        for command in subsequent_steps:
                            logger.info(f"ADICIONANDO COMANDO CLI: {file} {command['input']}")
                            self.roadmap.append({
                                "info": command.get("info", f"comando '{command['input']}' retorna '{command['expected']}'"),
                                "args": [current_file_path, command["input"].split(" "), command["expected"]],
                                "action": test_CLI
                            })
                    elif check_step == "STRUCTURE":
                        try:
                            importedFile = Imported(current_file_path)
                        except Exception as e:
                            logger.warning(f"Falha ao importar o arquivo '{file}': {e}")
                            importedFile = SimpleNamespace(module=None, logger=logger)
                        if subsequent_steps.get("CLASSES"):
                            logger.info(f"CLASSES DETECTADAS")
                            for class_info in subsequent_steps["CLASSES"]:
                                logger.info(f"ADICIONANDO CLASSE {class_info['name']}")
                                is_initialized = class_info.get("initialized", False)
                                has_methods = class_info.get("methods", []) != []
                                currentClass = ClassTester(importedFile, class_info["name"], class_info["methods"] if has_methods else [], is_initialized)
                                self.roadmap.append({
                                    "info": class_info.get("info", f"classe {class_info['name']} existe e possui os métodos esperados"),
                                    "args": [currentClass],
                                    "action": ClassTester.get_existance
                                })
                                if is_initialized:
                                    self.roadmap.append({
                                        "info": class_info.get("info", f"classe {class_info['name']} pode ser instanciada"),
                                        "args": [currentClass, *class_info["initializer"]["input"]],
                                        "action": ClassTester.initialize_instance
                                    })
                                if has_methods:
                                    for method_info in class_info["methods"]:
                                        self.roadmap.append({
                                            "info": method_info.get("info", f"{method_info['name']}({', '.join(map(str, method_info['input']))}) retorna {method_info['expected']}"),
                                            "args": [method_info["name"], method_info.get("static", False), method_info["input"], method_info["expected"]],
                                            "action": currentClass.test_method
                                        })
                        if subsequent_steps.get("FUNCTIONS"):
                            logger.info(f"FUNÇÕES DETECTADAS")
                            for function_info in subsequent_steps["FUNCTIONS"]:
                                logger.info(f"ADICIONANDO FUNÇÃO {function_info['name']}")
                                currentFunction = FunctionTester(importedFile, function_info["name"])
                                self.roadmap.append({
                                    "info": function_info.get("info", f"função {function_info['name']} existe"),
                                    "args": [currentFunction],
                                    "action": FunctionTester.get_existance
                                })
                                for run in function_info["runs"]:
                                    logger.info(f"ADICIONANDO RUN {function_info['name']}({', '.join(map(str, run['input']))})")
                                    self.roadmap.append({
                                        "info": run.get("info", f"função {function_info['name']}({', '.join(map(str, run['input']))}) retorna {run['expected']}"),
                                        "args": [currentFunction, run["input"], run["expected"]],
                                        "action": FunctionTester.test
                                    })
                    elif check_step == "INPUTS" or check_step == "SEQUENCE_INPUTS":
                        for sequence_input_info in subsequent_steps:
                            logger.info(f"ADICIONANDO INPUTS {sequence_input_info['input']}")

                            expected = sequence_input_info['expected']
                            input_data = sequence_input_info['input']

                            if isinstance(expected, str):
                                expected = [expected]
                            if isinstance(input_data, str):
                                input_data = [input_data]

                            self.roadmap.append({
                                "info": sequence_input_info.get("info", f"input '{', '.join(input_data)}' retorna '{', '.join(expected)}'"),
                                "args": [current_file_path, input_data, expected],
                                "action": test_INPUTS
                            })
                    else:
                        raise ValueError(f"Característica desconhecida '{check_step}' no arquivo de correção")
        except (ValueError, KeyError) as e:
            logger.error(f"Estrutura do arquivo de correção inválida para o arquivo '{file}'.\nDetalhes: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao configurar roadmap para o arquivo '{file}'.")
            logger.error(f"Detalhes do erro: {e}\n{traceback.format_exc()}")
            return False

        return True

    def make_result_message(self, result: Result, info: str) -> str:
        """Forma uma mensagem de resultado com cores e estilo apropriados

        Args:
            result (Result): Resultado do teste
            info (str): Informação sobre o teste realizado

        Returns:
            str: Mensagem formatada
        """
        colors = {
            True: Fore.GREEN,
            False: Fore.RED
        }
        return f"{colors[result.success]}{Style.BRIGHT}{':)' if result.success else ':('}{Style.RESET_ALL} {colors[result.success]}{info}{Style.RESET_ALL}{f'\n{Fore.RED}{Style.DIM}   ↳ ERRO: {result.error.replace('\n', '  ')}{Style.RESET_ALL}' if result.error != '' else ''}"


    def run_roadmap(self) -> tuple[int, list[Result]]:
        """Executa os testes do roadmap e retorna uma lista de resultados

        Returns:
            tuple[bool, list[Result]]: Tupla contendo um int com valor para sys.exit() indicando se todos os testes passaram e uma lista de resultados
        """
        all_passed = 0
        results = []
        for step in self.roadmap:
            logger.debug(f"Executando teste {step['info']} com argumentos {', '.join(str(arg) for arg in step['args'])}")
            try:
                logger.debug(step["args"])
                result = step["action"](*step["args"])
                if not result.success:
                    all_passed = 1
            except Exception as e:
                result = Result(False, f"Erro inesperado: {traceback.format_exc()}")
                logger.warning(f"Erro ao executar o teste '{step['info']}': {e}\n{traceback.format_exc()}")
                all_passed = 1
            
            results.append(self.make_result_message(result, step["info"]))

        return (all_passed, results)

    
    def show_results(self, results: list) -> bool:
        """Exibe os resultados dos testes no console

        Args:
            results (list): Lista de resultados dos testes
        """
        if self.answers.get("description"):
            print(f"{self.answers['description']}")
        for result in results:
            print(result)