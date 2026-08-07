import importlib.util
import logging
import traceback
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO


def _call_with_captured_output(callable_obj, *args, **kwargs):
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        result = callable_obj(*args, **kwargs)

    return result, stdout_buffer.getvalue().strip(), stderr_buffer.getvalue().strip()

class Imported:
    def __init__(self, module_path: str):
        self.logger = logging.getLogger(__name__)
        self.module = self.__import_module(module_path)

    def __import_module(self, module_path: str):
            """Importa um módulo Python a partir de um caminho de arquivo
    
            :param module_path: Caminho do arquivo do módulo
            :returns: O módulo importado
            :rtype: module
            :raises ImportError: Se não for possível importar o módulo
            """
            try:
                spec = importlib.util.spec_from_file_location("module_custom", module_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Não foi possível criar o carregador do módulo '{module_path}'")

                module = importlib.util.module_from_spec(spec)
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    spec.loader.exec_module(module)
                return module
            except Exception as e:
                self.logger.error(f"Falha ao importar o módulo '{module_path}': {e}")
                raise ImportError(f"Falha ao importar o módulo '{module_path}'") from e

class ClassTester:
    def __init__(self, import_info: Imported, class_name: str, methods: list, initialized: bool):
        self.import_info = import_info
        self.class_name = class_name
        self.methods = methods
        self.initialized = initialized
        self.exists = self.check_existance()
        self.instance = None

    def check_existance(self):
        """Testa se a classe existe e se possui os métodos esperados"""
        cls = getattr(self.import_info.module, self.class_name, None)
        if cls is None:
            self.import_info.logger.warning(f"A classe '{self.class_name}' não foi encontrada no módulo.")
            return False

        for method in self.methods:
            if not hasattr(cls, method["name"]):
                self.import_info.logger.warning(f"O método '{method['name']}' não foi encontrado na classe '{self.class_name}'.")
                return False

        return True

    def initialize_instance(self, *args) -> bool:
        """Inicializa uma instância da classe com os argumentos fornecidos"""
        if not self.exists:
            self.import_info.logger.warning(f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")
            return False

        cls = getattr(self.import_info.module, self.class_name, None)
        try:
            self.instance = cls(*args)
        except Exception as e:
            self.import_info.logger.warning(f"Falha ao inicializar a instância da classe '{self.class_name}': {e}")
            return False

        return True

    def get_existance(self):
        """Retorna se a classe existe e possui os métodos esperados"""
        return self.exists

    def test_method(self, method_name: str, static: bool, input_args: list, expected_output):
        """Testa se um método da classe retorna o valor esperado"""
        if not self.exists:
            self.import_info.logger.warning(f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")
            return False

        try:
            cls = getattr(self.import_info.module, self.class_name, None)
            method = getattr(cls, method_name, None)

            if not static and self.instance is not None:
                result, captured_stdout, _ = _call_with_captured_output(method, self.instance, *input_args)
            else:
                result, captured_stdout, _ = _call_with_captured_output(method, *input_args)

            observed_output = result if result is not None else captured_stdout
            if observed_output != expected_output and str(observed_output) != str(expected_output):
                self.import_info.logger.warning(f"O método '{method_name}' retornou '{observed_output}', mas era esperado '{expected_output}'.")
                return False
        except Exception as e:
            self.import_info.logger.warning(f"Falha ao testar o método '{method_name}': {e}")
            self.import_info.logger.warning(f"Traceback: {traceback.format_exc()}")
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
            self.import_info.logger.warning(f"A função '{self.function_name}' não foi encontrada no módulo.")
            return False

        return True

    def get_existance(self):
        """Retorna se a função existe"""
        return self.exists

    def test(self):
        """Testa se a função retorna o valor esperado"""
        if not self.exists:
            self.import_info.logger.info(f"A função '{self.function_name}' não existe.")
            return False

        try:
            func = getattr(self.import_info.module, self.function_name, None)
            result, captured_stdout, _ = _call_with_captured_output(func, *self.input_args)
            observed_output = result if result is not None else captured_stdout
            if observed_output != self.expected_output and str(observed_output) != str(self.expected_output):
                self.import_info.logger.warning(f"A função '{self.function_name}' retornou '{observed_output}', mas era esperado '{self.expected_output}'.")
                return False
        except Exception as e:
            self.import_info.logger.warning(f"Falha ao testar a função '{self.function_name}': {e}")
            self.import_info.logger.warning(f"Traceback: {traceback.format_exc()}")
            return False

        return True