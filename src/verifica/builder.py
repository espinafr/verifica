from pathlib import Path
from colorama import Style, Fore, init
from functools import wraps
import subprocess
import os

from tui import TUI
from config import settings

init(autoreset=True)

class Controller:
    @staticmethod
    def clear_command():
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'cls'])
        else:
            subprocess.run(['clear'])


    def clear_terminal(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Controller.clear_command()
            return func(*args, **kwargs)
        return wrapper


    def sequential_question(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answers = []
            while True:
                result = func(*args, **kwargs)
                if result.strip() != "":
                    answers.append(result)
                else:
                    return answers
        return wrapper


    def required_question(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                result = func(*args, **kwargs)
                if not isinstance(result, str) or result.strip() == "":
                    print(f"{Style.BRIGHT}{Fore.RED}Este campo é obrigatório. Por favor, insira um valor válido.{Style.RESET_ALL}")
                else:
                    return result
        return wrapper


    def required_text(text) -> str:
        return f"{Fore.RED}{text}{Style.RESET_ALL}"


    def optional_text(text) -> str:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"


    def sequence_text(text) -> str:
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


class Selector:
    def __init__(self, name: str, action: function, selected: bool = False):
        self.name = name
        self.action = action
        self.selected = selected

class FileBuilder(Controller):
    def __init__(self, file: str):
        self.file = file
        self.Selectors = [
            Selector("Classe", self.create_classes),
            Selector("Função", self.create_functions),
            Selector("CLI", self.create_cli),
            Selector("Input", self.create_inputs),
            Selector("Input sequencial", self.create_sequence_inputs)
        ]
        self.current_file = {}


    @Controller.clear_terminal
    def show_selector(self):
        if not hasattr(self, 'tui'):
            self.tui = TUI([self.file, {"":f"Selecione o tipo de parâmetro que você quer analisar para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}. Digite o número correspondente e aperte ENTER."}, {}], max_line=50)

        for index, selector in enumerate(self.Selectors):
            self.tui.contents[2][f"{Style.BRIGHT}{Fore.CYAN}[{index + 1}]"] = f"{Fore.GREEN if selector.selected else Fore.WHITE}{selector.name}"

        self.tui.show()


    def index_is_selectable(self, index: int) -> bool:
        try:
            index = int(index)
            available_selectors = len(self.Selectors)
            if index <= available_selectors and index >= 0:
                return True
            else:
                return False
        except ValueError:
            return False


    def get_selectors(self):
        self.show_selector()
        selecteds = 0
        while True:
            index = Controller.required_question(input)(Controller.required_text("> "))
            if self.index_is_selectable(index):
                self.Selectors[int(index) - 1].selected = True
                selecteds += 1
                break

        self.show_selector()
        while True:
            index = input(Controller.optional_text("> "))
            if index.strip() != "":
                if self.index_is_selectable(index):
                    index = int(index)
                    self.Selectors[index - 1].selected = not self.Selectors[index - 1].selected
                    if self.Selectors[index - 1].selected:
                        selecteds += 1
                    else:
                        selecteds -= 1
                    self.show_selector()
                else:
                    print(Controller.required_text("Indice inválido."))
            else:
                if selecteds == 0:
                    print(Controller.required_text("Pelo menos um item deve ser selecionado."))
                else:
                    return


    def create_structure(self):
        if not "STRUCTURE" in self.current_file:
            self.current_file["STRUCTURE"] = {}
        return True


    def create_classes(self):
        self.create_structure()
        if not "CLASSES" in self.current_file["STRUCTURE"]:
            self.current_file["STRUCTURE"]["CLASSES"] = []

        print(f"Iniciando criação de classes para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}.")
        while True:
            current_class = {}
            class_name = Controller.required_question(input)(Controller.required_text("Nome da classe: "))
            current_class["name"] = class_name

            is_initialized = Controller.required_question(input)(Controller.required_text("A classe possui um método __init__? (s/n): "))
            if is_initialized[0].strip().lower() == "s":
                current_class["initializer"] = {}
                current_class["initialized"] = True
                while True:
                    print("Digite os parâmetros do método __init__ (um por vez). Para parar, aperte ENTER sem digitar nada: ")
                    args = Controller.sequential_question(input)(Controller.optional_text("> "))
                    current_class["initializer"]["args"] = args if args else []

                    print("Descrição da classe: ")
                    class_info = input(Controller.optional_text("> "))
                    if class_info.strip() != "":
                        current_class["initializer"]["info"] = class_info
                    break

            while True:
                add_method = Controller.required_question(input)(Controller.required_text("Deseja adicionar um método à classe? (s/n): "))
                if add_method[0].lower() == "s":
                    if not "methods" in current_class:
                        current_class["methods"] = []

                    method_name = Controller.required_question(input)(Controller.required_text("Nome do método: "))

                    method_info = input(Controller.optional_text("Descrição do método: "))

                    method_args = Controller.sequential_question(input)(Controller.optional_text("Digite os parâmetros do método (um por vez). Para parar, aperte ENTER sem digitar nada: "))

                    method_data = {
                        "name": method_name,
                        "args": method_args if method_args else []
                    }
                    if method_info.strip() != "":
                        method_data["info"] = method_info
                    current_class["methods"].append(method_data)
                else:
                    break

            self.current_file["STRUCTURE"]["CLASSES"].append(current_class)
            print(f"Classe {Style.BRIGHT}{Fore.CYAN}{class_name}{Style.RESET_ALL} adicionada com sucesso!")
            new_class = Controller.required_question(input)(Controller.required_text("Deseja adicionar outra classe? (s/n): "))
            if new_class[0].strip().lower() != "s":
                break
            


    def create_functions(self):
        self.create_structure()
        if not "FUNCTIONS" in self.current_file["STRUCTURE"]:
            self.current_file["STRUCTURE"]["FUNCTIONS"] = []

        while True:
            current_function = {}
            function_name = Controller.required_question(input)(Controller.required_text("Nome da função: "))
            current_function["name"] = function_name

            print("Execuções de teste da função:")
            current_function["runs"] = {}
            while True:
                inputs = Controller.sequential_question(input)(Controller.optional_text("Digite os inputs de teste da função (um por vez). Para parar, aperte ENTER sem digitar nada: "))
                current_function["runs"]["inputs"] = inputs if inputs else []

                expected = Controller.required_question(input)(Controller.required_text("Digite o output esperado da função: "))
                current_function["runs"]["expected"] = expected

                info = input(Controller.optional_text("Descrição da função: "))
                if info.strip() != "":
                    current_function["info"] = info
        
        

    def create_cli(self):
        pass


    def create_inputs(self):
        pass


    def create_sequence_inputs(self):
        pass


    def purge_unselected(self):
        selected = []
        for selector in self.Selectors:
            if selector.selected:
                selected.append(selector)
        self.Selectors = selected


    def run_selected(self):
        for selector in self.Selectors:
            selector.action()


    def start(self):
        self.get_selectors()
        self.purge_unselected()
        self.run_selected()


class Builder:
    default_info =[
        f"{Fore.YELLOW}{Style.BRIGHT}Gerador de {settings.get_config("answers_file_name")}",
        f"{Style.DIM}Seu progresso vai ficar aqui.",
        {
            f"{Style.BRIGHT}{Fore.RED}Informações importantes:": "", 
            f"{Style.BRIGHT}{Fore.CYAN}1.": "Leia atentamente a todos os avisos e instruções antes de prosseguir.", 
            f"{Style.BRIGHT}{Fore.CYAN}2.": f"Inputs {Fore.RED}VERMELHOS{Style.RESET_ALL} são obrigatórios, enquanto inputs {Fore.YELLOW}AMARELOS{Style.RESET_ALL} são opcionais.", 
            f"{Style.BRIGHT}{Fore.CYAN}3.": f"Alguns inputs exigem uma sequência de informções. Esses serão indicados com {Fore.GREEN}setas verdes (>){Style.RESET_ALL}. Quando quiser parar de adicionar informações, basta apertar {Style.BRIGHT}ENTER{Style.RESET_ALL} sem digitar nada enquanto a seta estiver {Fore.YELLOW}AMARELA (>){Style.RESET_ALL}.",
        }
    ]

    @staticmethod
    def confirm_yield():
        input("Pressione ENTER para continuar...")

    def __init__(self, location: Path):
        self.location = location
        self.build = {}
        self.info = TUI(self.default_info, max_line=80)
    
    @Controller.clear_terminal
    def show_info(self):
        self.info.show()
    
    def add_block(self, name: str, content: str):
        self.build[name] = content

    def show_progress(self, name: str, text: str):
        progress = self.info.contents[1]
        if not isinstance(progress, dict):
            progress = {}

        progress[f"{Style.BRIGHT}{name}"] = text
        self.info.contents[1] = progress

        self.show_info()

    def get_files(self):
        files = []

        def format_filename(filename: str) -> str:
            if not filename.endswith(".py"):
                filename += ".py"
            return filename

        print(f"Vamos começar nomeando os arquivos que você quer analisar. O primeiro arquivo é obrigatório, então digite o nome dele e aperte ENTER.\n{Fore.YELLOW}OBSERVAÇÃO: A extensão .py será adicionada automaticamente.")
        files.append(format_filename(Controller.required_question(input)(f"{Controller.required_text('Nome do primeiro arquivo: ')}")))
        print("Perfeito! Agora, se quiser adicionar mais arquivos, digite o nome deles um por vez. Para parar aperte ENTER sem digitar nada.")
        files.extend(list(map(format_filename, Controller.sequential_question(input)(f"{Controller.optional_text('> ')}"))))
        
        return list(dict.fromkeys(files))

    def file_selection(self, file):
        current_file = {}
        TUI([file, f"Selecione o tipo de parâmetro que você quer analisar para o arquivo {Style.BRIGHT}{Fore.CYAN}{file}{Style.RESET_ALL}. Digite o número correspondente e aperte ENTER.", {
            f"{Style.BRIGHT}{Fore.CYAN}[1]": "Classe",
            f"{Style.BRIGHT}{Fore.CYAN}[2]": "Função",
            f"{Style.BRIGHT}{Fore.CYAN}[3]": "CLI",
            f"{Style.BRIGHT}{Fore.CYAN}[4]": "Input",
            f"{Style.BRIGHT}{Fore.CYAN}[5]": "Input sequencial"
        }], max_line=80)

        """
            Faz um renderizador de dicionário que pega os inputs do usuário e os exibe no TUI mudando de cor conforme seleção
            Lembra de fazer algo que permita que o usuário desselecione algo
        """

    def start(self):
        self.show_info()

        files = self.get_files()
        self.add_block("files", files)
        self.show_progress("Arquivos selecionados: ", f"{'; '.join(files)}.")
        self.confirm_yield()

        Controller.clear_command()
        for file in files:
            fb = FileBuilder(file)
            fb.start()

oi = Builder(Path.cwd())
oi.start()