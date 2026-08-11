from colorama import Style, Fore
from functools import wraps
from pathlib import Path
import subprocess
import json
import sys
import os

from .tui import TUI, ANSI_PATTERN
from .config import settings

# Código ANSI para limpar a linha atual no terminal
CLEAR_LINE = "\r\033[K"

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


    def loop_breaker(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                return None
        return wrapper


    def sequential_question(input_text):
        answers = []
        try:
            while True:
                result = input(input_text)
                answers.append(result)

                # Altera a linha anterior para explicitar que foi salvo
                sys.stdout.write("\033[F\033[K")
                sys.stdout.flush()
                print(f"{Fore.GREEN}{ANSI_PATTERN.sub('', input_text)}{result}{Style.RESET_ALL}")
        except KeyboardInterrupt:
            return answers


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
    def __init__(self, name: str, action, selected: bool = False):
        self.name = name
        self.action = action
        self.selected = selected

class FileBuilder(Controller):
    def __init__(self, file: str):
        self.file = file
        self.selectors = [
            Selector("Classe", self.create_classes),
            Selector("Função", self.create_functions),
            Selector("CLI", self.create_cli),
            Selector("Inputs", self.create_inputs),
        ]
        self.current_file = {}


    @Controller.clear_terminal
    def show_selector(self):
        if not hasattr(self, 'tui'):
            self.tui = TUI([self.file, {"":f"Selecione o tipo de funcionalidade que você quer testar no arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}. Digite o número correspondente e aperte ENTER."}, {}], max_line=50)

        for index, selector in enumerate(self.selectors):
            self.tui.contents[2][f"{Style.BRIGHT}{Fore.CYAN}[{index + 1}]"] = f"{Fore.GREEN if selector.selected else Fore.WHITE}{selector.name}"

        self.tui.show()


    def index_is_selectable(self, index: int) -> bool:
        try:
            index = int(index)
            available_selectors = len(self.selectors)
            if index <= available_selectors and index >= 1:
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
                self.selectors[int(index) - 1].selected = True
                selecteds += 1
                break

        self.show_selector()
        while True:
            index = input(Controller.optional_text("> "))
            if index.strip() != "":
                if self.index_is_selectable(index):
                    index = int(index)
                    self.selectors[index - 1].selected = not self.selectors[index - 1].selected
                    if self.selectors[index - 1].selected:
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


    @Controller.clear_terminal
    def create_classes(self):
        self.create_structure()
        if not "CLASSES" in self.current_file["STRUCTURE"]:
            self.current_file["STRUCTURE"]["CLASSES"] = []

        print(f"Iniciando registro de classes para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}.")
        while True:
            current_class = {}
            class_name = Controller.required_question(input)(Controller.required_text("Nome da classe: "))
            current_class["name"] = class_name

            is_initialized = Controller.required_question(input)(Controller.required_text("A classe possui um método __init__? (s/n): "))
            if is_initialized.strip()[0].lower() == "s":
                current_class["initializer"] = {}
                current_class["initialized"] = True
                while True:
                    print(f"Digite os parâmetros do método __init__ (um por vez). {Style.DIM}Aperte CTRL-C para parar.")
                    inputs = Controller.sequential_question(Controller.optional_text("> "))
                    current_class["initializer"]["input"] = inputs if inputs else []

                    class_info = input(Controller.optional_text(f"{CLEAR_LINE}Descrição da validação (instancialização da classe): "))
                    if class_info.strip() != "":
                        current_class["initializer"]["info"] = class_info
                    break

            while True:
                add_method = Controller.required_question(input)(Controller.required_text("Deseja adicionar um método à classe? (s/n): "))
                if add_method[0].lower() == "s":
                    if not "methods" in current_class:
                        current_class["methods"] = []
                    method_data = {}

                    method_name = Controller.required_question(input)(Controller.required_text("Nome do método: "))
                    method_data["name"] = method_name

                    print(f"Digite os parâmetros do método {Style.DIM}Aperte CTRL-C para parar.")
                    method_inputs = Controller.sequential_question(Controller.optional_text("> "))
                    method_data["input"] = method_inputs if method_inputs else []

                    is_static = Controller.required_question(input)(Controller.required_text(f"{CLEAR_LINE}O método é estático? (s/n): "))
                    method_data["static"] = True if is_static.strip()[0].lower() == "s" else False

                    expected_output = input(Controller.optional_text("Output esperado: "))
                    method_data["expected"] = expected_output if expected_output else ""

                    method_info = input(Controller.optional_text("Descrição da validação: "))
                    if method_info.strip() != "":
                        method_data["info"] = method_info
                    current_class["methods"].append(method_data)
                else:
                    break
            
            self.current_file["STRUCTURE"]["CLASSES"].append(current_class)
            print(f"Classe {Style.BRIGHT}{Fore.CYAN}{class_name}{Style.RESET_ALL} adicionada com sucesso!")
            new_class = Controller.required_question(input)(Controller.required_text("Deseja adicionar outra classe? (s/n): "))
            if new_class.strip()[0].lower() != "s":
                break
            


    @Controller.clear_terminal
    def create_functions(self):
        self.create_structure()
        if not "FUNCTIONS" in self.current_file["STRUCTURE"]:
            self.current_file["STRUCTURE"]["FUNCTIONS"] = []

        print(f"Iniciando registro de funções para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}.")
        while True:
            current_function = {}
            function_name = Controller.required_question(input)(Controller.required_text("Nome da função: "))
            current_function["name"] = function_name

            print("Bateria de testes da função")
            current_function["runs"] = []
            while True:
                current_run = {}

                print(f"Digite os inputs necessários para testar a função. {Style.DIM}Aperte CTRL-C para parar.")
                inputs = Controller.sequential_question(Controller.optional_text("> "))
                current_run["input"] = inputs if inputs else []

                expected = input(Controller.optional_text(f"{CLEAR_LINE}Output esperado: "))
                current_run["expected"] = expected if expected else ""

                info = input(Controller.optional_text("Descrição da validação: "))
                if info.strip() != "":
                    current_run["info"] = info

                current_function["runs"].append(current_run)
                new_run = Controller.required_question(input)(Controller.required_text("Deseja adicionar outra bateria de testes? (s/n): "))
                if new_run.strip()[0].lower() != "s":
                    break

            self.current_file["STRUCTURE"]["FUNCTIONS"].append(current_function)
            print(f"Função {Style.BRIGHT}{Fore.CYAN}{function_name}{Style.RESET_ALL} adicionada com sucesso!")

            new_class = Controller.required_question(input)(Controller.required_text("Deseja adicionar outra função? (s/n): "))
            if new_class.strip()[0].lower() != "s":
                break
        
        

    @Controller.clear_terminal
    def create_cli(self):
        self.current_file["CLI"] = []
        print(f"Iniciando registro de CLI para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}.")
        while True:
            current_cli = {}
            inputs = input(Controller.optional_text("Argumentos do comando: "))
            current_cli["input"] = inputs if inputs else ""

            expected = input(Controller.optional_text("Output esperado: "))
            current_cli["expected"] = expected if expected else ""

            info = input(Controller.optional_text("Descrição da validação: "))
            if info.strip() != "":
                current_cli["info"] = info

            self.current_file["CLI"].append(current_cli)
            print(f"{Style.BRIGHT}{Fore.CYAN}Comando registrado com sucesso!")
            new_run = Controller.required_question(input)(Controller.required_text("Deseja adicionar outro comando CLI? (s/n): "))
            if new_run.strip()[0].lower() != "s":
                break


    @Controller.clear_terminal
    def create_inputs(self):
        print(f"Iniciando registro de inputs para o arquivo {Style.BRIGHT}{Fore.CYAN}{self.file}{Style.RESET_ALL}.")
        self.current_file["INPUTS"] = []
        while True:
            current_seqinput = {}
            print(f"Digite os inputs. {Style.DIM}Aperte CTRL-C para parar.")
            inputs = Controller.sequential_question(Controller.optional_text("> "))
            current_seqinput["input"] = inputs if inputs else []

            print(f"{CLEAR_LINE}Digite os outputs esperados. {Style.DIM}Aperte CTRL-C para parar.")
            expected = Controller.sequential_question(Controller.optional_text("> "))
            current_seqinput["expected"] = expected if expected else []

            info = input(Controller.optional_text(f"{CLEAR_LINE}Descrição da validação: "))
            if info.strip() != "":
                current_seqinput["info"] = info

            self.current_file["INPUTS"].append(current_seqinput)
            print(f"{Style.BRIGHT}{Fore.CYAN}Input registrado com sucesso!")
            new_run = Controller.required_question(input)(Controller.required_text("Deseja adicionar outro input? (s/n): "))
            if new_run.strip()[0].lower() != "s":
                break


    def purge_unselected(self):
        selected = []
        for selector in self.selectors:
            if selector.selected:
                selected.append(selector)
        self.selectors = selected


    def run_selected(self):
        for selector in self.selectors:
            selector.action()


    def show_progress(self):
        TUI([f"{Fore.CYAN}{self.file}", *({f"{Fore.CYAN}[{index+1}]": f"{Fore.GREEN}{key}{Style.RESET_ALL} {self.current_file[key]}"} for index, key in enumerate(self.current_file.keys()))], max_line=50).show()
    

    def start(self):
        self.get_selectors()
        self.purge_unselected()
        self.run_selected()
        self.show_progress()


class Builder:
    default_info =[
        f"{Fore.YELLOW}{Style.BRIGHT}Gerador de {settings.get_config("answers_file_name")}",
        f"{Style.DIM}Seu progresso vai ficar aqui.",
        {
            f"{Style.BRIGHT}{Fore.RED}Informações importantes:": "", 
            f"{Style.BRIGHT}{Fore.CYAN}1.": "Leia atentamente a todos os avisos e instruções antes de prosseguir.", 
            f"{Style.BRIGHT}{Fore.CYAN}2.": f"Inputs {Fore.RED}VERMELHOS{Style.RESET_ALL} são obrigatórios, enquanto inputs {Fore.YELLOW}AMARELOS{Style.RESET_ALL} são opcionais.", 
            f"{Style.BRIGHT}{Fore.CYAN}3.": f"Alguns inputs exigem uma sequência de informções. Esses serão indicados com {Style.BRIGHT}setas (>){Style.RESET_ALL}.\nPara esse tipo de input, digite cada informação e aperte ENTER para confirmar. Inputs registrados com sucesso ficarão {Fore.GREEN}verdes{Style.RESET_ALL}.\nPara parar de adicionar informações, aperte {Style.BRIGHT}CTRL-C{Style.RESET_ALL} (salvo em situações que explicitamente indiquem o contrário).",
        }
    ]

    @staticmethod
    def confirm_yield():
        input("Pressione ENTER para continuar...")

    def __init__(self):
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

        def get_extra_files() -> list:
            extra_files = []
            while True:
                extra_file = input(f"{Controller.optional_text('> ')}")
                if extra_file.strip() != "":
                    extra_files.append(format_filename(extra_file))
                else:
                    break
            return extra_files

        print(f"\nNomeie os arquivos que você quer analisar. O primeiro arquivo é obrigatório.\n{Fore.YELLOW}OBSERVAÇÃO: A extensão .py será adicionada automaticamente.")
        files.append(format_filename(Controller.required_question(input)(f"{Controller.required_text('Nome do primeiro arquivo: ')}")))
        print(f"\nSe quiser adicionar mais arquivos, digite o nome deles um por vez.\n{Style.DIM}Para parar aperte ENTER sem digitar nada.")
        files.extend(get_extra_files())
        
        return list(dict.fromkeys(files))


    @Controller.clear_terminal
    def save_file(self):
        assignment_name = Controller.required_question(input)(f"{Controller.required_text('Nome da atividade: ')}")
        save_path = Path.cwd() / assignment_name

        print(f"O arquivo \"correcao.json\" será salvo em {save_path}.")
        change_path = input(f"{Controller.optional_text('Deseja alterar o caminho? (s/n): ')}")

        if change_path and change_path.strip()[0].lower() == "s":
            user_input = Controller.required_question(input)(f"{Controller.required_text('Novo caminho: ')}")
            save_path = Path(user_input)

        file_path = save_path / "correcao.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.build, file, indent=4, ensure_ascii=False)

        print(f"Arquivo salvo em {file_path}.")

    def start(self):
        try:
            self.show_info()

            self.confirm_yield()
            files = self.get_files()
            self.add_block("files", files)
            self.show_progress("Arquivos selecionados: ", f"{'; '.join(files)}.")
            self.confirm_yield()

            Controller.clear_command()
            for file in files:
                fb = FileBuilder(file)
                fb.start()
                self.add_block(file, fb.current_file)

                self.confirm_yield()

            self.save_file()
        except KeyboardInterrupt:
            Controller.clear_command()
            print(f"{Fore.RED}Operação cancelada pelo usuário. Nenhum arquivo foi salvo.")