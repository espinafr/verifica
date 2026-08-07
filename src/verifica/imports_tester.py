import importlib.util
import logging

class Imported:
    def __init__(self, module_path: str):
        self.module = self.__import_module(module_path)
        self.logger = logging.getLogger(__name__)

    def __import_module(self, module_path: str):
            """Importa um módulo Python a partir de um caminho de arquivo
    
            :param module_path: Caminho do arquivo do módulo
            :returns: O módulo importado
            :rtype: module
            :raises ImportError: Se não for possível importar o módulo
            """
            try:
                spec = importlib.util.spec_from_file_location("module", module_path)
                return importlib.util.module_from_spec(spec)
            except ImportError as e:
                self.logger.error(f"Falha ao importar o módulo '{module_path}': {e}")
                raise ImportError(f"Falha ao importar o módulo '{module_path}'") from e

class ClassTester:
    def __init__(self, import_info: Imported, class_name: str, methods: list):
        self.import_info = import_info
        self.class_name = class_name
        self.methods = methods
        self.exists = self.check_existance()

    def check_existance(self):
        """Testa se a classe existe e se possui os métodos esperados"""
        cls = getattr(self.import_info.module, self.class_name, None)
        if cls is None:
            self.logger.error(f"A classe '{self.class_name}' não foi encontrada no módulo.")
            return False

        for method in self.methods:
            if not hasattr(cls, method["name"]):
                self.logger.error(f"O método '{method['name']}' não foi encontrado na classe '{self.class_name}'.")
                return False

        return True

    def get_existance(self):
        """Retorna se a classe existe e possui os métodos esperados"""
        return self.exists

    def test_method(self, method_name: str, input_args: list, expected_output):
        """Testa se um método da classe retorna o valor esperado"""
        if not self.exists:
            self.logger.info(f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")
            return False

        cls = getattr(self.import_info.module, self.class_name, None)
        method = getattr(cls, method_name, None)
        instance = getattr(self.import_info.module, self.class_name, None)

        result = method(instance, *input_args)
        if result != expected_output:
            self.logger.error(f"O método '{method_name}' retornou '{result}', mas era esperado '{expected_output}'.")
            return False

        return True

class FunctionTester:
    def __init__(self, import_info: Imported, function_name: str, input_args: list, expected_output):
        self.import_info = import_info
        self.function_name = function_name
        self.input_args = input_args
        self.expected_output = expected_output
        self.exists = self.check_existance()

    def check_existance(self):
        """Testa se a função existe"""
        func = getattr(self.import_info.module, self.function_name, None)
        if func is None:
            self.logger.error(f"A função '{self.function_name}' não foi encontrada no módulo.")
            return False

        return True

    def get_existance(self):
        """Retorna se a função existe"""
        return self.exists

    def test(self):
        """Testa se a função retorna o valor esperado"""
        if not self.exists:
            self.logger.info(f"A função '{self.function_name}' não existe.")
            return False

        func = getattr(self.import_info.module, self.function_name, None)
        result = func(*self.input_args)
        if result != self.expected_output:
            self.logger.error(f"A função '{self.function_name}' retornou '{result}', mas era esperado '{self.expected_output}'.")
            return False

        return True