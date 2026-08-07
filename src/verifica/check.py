from colorama import Fore, Style
from pathlib import Path
import subprocess
import traceback
import logging
import sys

from . import imports_tester
from .config import settings

class Checker:

    def __init__(self, exercises_path: str, answers: dict):
        """Atribui os parâmetros passados para o objeto
        
        :param exercises_path: Caminho da pasta com arquivos do exercício
        :param answers: Dicionário de respostas no formato apropriado
        """
        self.exercises_path = exercises_path
        self.answers = answers
        self.roadmap = []
        self.logger = logging.getLogger(__name__)
    
    def __file_exists(self, file_path: str) -> bool:
        """Checa se um arquivo existe em determinado caminho

        :param file_path: Caminho do arquivo
        :returns: Verdadeiro caso exista
        :rtype: bool
        """
        return Path(self.exercises_path / file_path).is_file()

    def setup_roadmap(self) -> None:
        """Popula a lista roadmap com uma sequência de testes a serem realizados"""
        try:
            self.logger.info(f"Configurando roadmap")
            for file in self.answers["files"]:
                current_file_path = Path(self.exercises_path) / file
                self.logger.info(f"Inicindo detecções para o arquivo '{file}'")

                if len(self.answers[file]) == 0:
                    raise ValueError(f"O arquivo de correção para '{file}' não possui características a serem testadas")

                self.logger.info(file)
                self.roadmap.append({
                    "info": f"'{file}' existe",
                    "args": [self, file],
                    "action": Checker.__file_exists
                })

                for check_step, subsequent_steps in self.answers[file].items():
                    self.logger.info(f"CARACTERÍSTICA DETECTADA: {check_step}")
                    if check_step == "CLI":
                        for command in subsequent_steps:
                            self.logger.info(f"ADICIONANDO COMANDO CLI: {file} {command['input']}")
                            self.roadmap.append({
                                "info": command.get("info", f"comando '{command['input']}' retorna '{command['expected']}'"),
                                "args": [current_file_path, command["input"].split(" "), command["expected"]],
                                "action": self.test_CLI
                            })
                    elif check_step == "STRUCTURE":
                        importedFile = imports_tester.Imported(current_file_path)
                        if subsequent_steps.get("CLASSES"):
                            self.logger.info(f"CLASSES DETECTADAS")
                            for class_info in subsequent_steps["CLASSES"]:
                                self.logger.info(f"ADICIONANDO CLASSE {class_info['name']}")
                                is_initialized = class_info.get("initialized", False)
                                currentClass = imports_tester.ClassTester(importedFile, class_info["name"], class_info["methods"], is_initialized)
                                self.roadmap.append({
                                    "info": class_info.get("info", f"classe {class_info['name']} existe e possui os métodos esperados"),
                                    "args": [currentClass],
                                    "action": imports_tester.ClassTester.get_existance
                                })
                                if is_initialized:
                                    self.roadmap.append({
                                        "info": class_info.get("info", f"classe {class_info['name']} pode ser instanciada"),
                                        "args": [currentClass, *class_info["initializer"]["args"]],
                                        "action": imports_tester.ClassTester.initialize_instance
                                    })
                                for method_info in class_info["methods"]:
                                    self.roadmap.append({
                                        "info": method_info.get("info", f"{method_info['name']}({', '.join(map(str, method_info['input']))}) retorna {method_info['expected']}"),
                                        "args": [method_info["name"], method_info.get("static", False), method_info["input"], method_info["expected"]],
                                        "action": currentClass.test_method
                                    })
                        if subsequent_steps.get("FUNCTIONS"):
                            self.logger.info(f"FUNÇÕES DETECTADAS")
                            for function_info in subsequent_steps["FUNCTIONS"]:
                                self.logger.info(f"ADICIONANDO FUNÇÃO {function_info['name']}")
                                currentFunction = imports_tester.FunctionTester(importedFile, function_info["name"], function_info["input"], function_info["expected"])
                                self.roadmap.append({
                                    "info": function_info.get("info", f"função {function_info['name']} existe"),
                                    "args": [currentFunction],
                                    "action": imports_tester.FunctionTester.get_existance
                                })
                                self.roadmap.append({
                                    "info": function_info.get("info", f"função {function_info['name']}({', '.join(map(str, function_info['input']))}) retorna {function_info['expected']}"),
                                    "args": [currentFunction],
                                    "action": imports_tester.FunctionTester.test
                                })
                    elif check_step == "INPUTS":
                        for input_info in subsequent_steps:
                            self.logger.info(f"ADICIONANDO INPUT {input_info['input']}")
                            self.roadmap.append({
                                "info": input_info.get("info", f"input '{input_info['input']}' retorna '{input_info['expected']}'"),
                                "args": [current_file_path, input_info["input"], input_info["expected"]],
                                "action": self.test_INPUT
                            })
                    elif check_step == "SEQUENCE_INPUTS":
                        for sequence_input_info in subsequent_steps:
                            self.logger.info(f"ADICIONANDO SEQUENCE_INPUTS {sequence_input_info['input']}")
                            self.roadmap.append({
                                "info": sequence_input_info.get("info", f"input '{sequence_input_info['input'].join(' -> ')}' retorna '{sequence_input_info['expected'].join(' -> ')}'"),
                                "args": [current_file_path, sequence_input_info["input"], sequence_input_info["expected"]],
                                "action": self.test_SEQUENCE_INPUT
                            })
                    else:
                        raise ValueError(f"Característica desconhecida '{check_step}' no arquivo de correção")
        except (ValueError, KeyError) as e:
            self.logger.error(f"Erro ao configurar roadmap: {e}\nEstrutura do arquivo de correção inválida para o arquivo '{file}'.")
        except Exception as e:
            self.logger.error(f"Erro ao configurar roadmap para o arquivo '{file}'.")
            self.logger.error(f"Detalhes do erro: {e}\n{traceback.format_exc()}")


    def test_CLI(self, input_args: list[str], expected_output: str) -> bool:
        try:
            result = subprocess.run([sys.executable] + input_args, capture_output=True, text=True)
            return result.stdout.strip() == expected_output
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"O script '{input_args[0]}' falhou com o código de saída {e.returncode}")
            self.logger.warning(f"Detalhes do erro: {e.stderr}")
            return False

    def test_INPUT(self, file: str, input_data: str, expected_output: str) -> bool:
        try:
            result = subprocess.run(
                [sys.executable, file], 
                input=input_data, 
                capture_output=True, 
                text=True
            )
            return expected_output in result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"A ação do input '{input_data}' falhou com o código de saída {e.returncode}")
            self.logger.warning(f"Detalhes do erro: {e.stderr}")
            return False

    def test_SEQUENCE_INPUT(self, file: str, input_data: list[str], expected_output: list[str]) -> bool:
        try:
            result = subprocess.run(
                [sys.executable, file], 
                input=input_data.join("\n"), 
                capture_output=True, 
                text=True
            )
            output = result.stdout.strip()
            return all(palavra in output for palavra in expected_output)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"A ação do input múltiplo '{input_data}' falhou com o código de saída {e.returncode}")
            self.logger.warning(f"Detalhes do erro: {e.stderr}")
            return False

    def run_roadmap(self) -> list:
        """Executa os testes do roadmap e retorna uma lista de resultados

        :returns: Lista de resultados dos testes
        :rtype: list
        """
        colors = {
            True: Fore.GREEN if settings.enviroment_supports_colors else "",
            False: Fore.RED if settings.enviroment_supports_colors else "",
            "bold": Style.BRIGHT if settings.enviroment_supports_colors else "",
            "reset": Style.RESET_ALL if settings.enviroment_supports_colors else ""
        }
        results = []
        for step in self.roadmap:
            try:
                self.logger.debug(step["args"])
                result = step["action"](*step["args"])
            except Exception as e:
                result = False
                self.logger.warning(f"Erro ao executar o teste '{step['info']}': {e}\n{traceback.format_exc()}")
            
            results.append(f"{colors[result]}{colors["bold"]}{':)' if result else ':('}{colors["reset"]}{colors[result]} {step['info']}{colors["reset"]}")

        return results

    def show_results(self, results: list) -> None:
        """Exibe os resultados dos testes no console

        :param results: Lista de resultados dos testes
        """
        if self.answers.get("description"):
            print(f"{self.answers['description']}")
        for result in results:
            print(result)