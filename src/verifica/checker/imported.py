import importlib.util
import logging
import traceback
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from .shared import Result, logger

def _call_with_captured_output(callable_obj, *args, **kwargs) -> tuple:
    """Chama uma função e captura a saída padrão e o erro padrão.

    Args:
        callable_obj: A função a ser chamada.
        *args: Argumentos posicionais para a função.
        **kwargs: Argumentos nomeados para a função.

    Returns:
        tuple: Uma tupla contendo o resultado da função, a saída padrão e o erro padrão.
    """
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        result = callable_obj(*args, **kwargs)

    return result, stdout_buffer.getvalue().strip(), stderr_buffer.getvalue().strip()

class Imported:
    def __init__(self, module_path: str):
        """Inicializa a instância da classe

        Args:
            module_path (str): Caminho do módulo a ser importado
        """
        self.module = self.__import_module(module_path)
        

    def __import_module(self, module_path: str) -> object:
        """Importa um módulo Python a partir de um caminho de arquivo

        Args:
            module_path (str): O módulo importado

        Raises:
            ImportError: Se não foi possível criar o carregador do módulo ou se ocorreu algum erro durante a importação
            ImportError: Se não for possível importar o módulo

        Returns:
            object: O módulo importado
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
            logger.warning(f"Falha ao importar o módulo '{module_path}': {e}")
            raise ImportError(f"Falha ao importar o módulo '{module_path}'") from e

class ClassTester:
    """Contempla a lógica de teste de uma classe importada de um módulo Python"""
    def __init__(self, import_info: Imported, class_name: str, methods: list = [], initialized: bool = False):
        """Inicializa a instância da classe

        Args:
            import_info (Imported): Informações do módulo importado
            class_name (str): Nome da classe
            methods (list, optional): Métodos a serem testados. O padrão é [].
            initialized (bool, optional): Se a instância da classe deve ser inicializada. O padrão é False.
        """
        self.import_info = import_info
        self.class_name = class_name
        self.methods = methods
        self.initialized = initialized
        self.exists = self.check_existance()
        self.instance = None

    def check_existance(self) -> Result:
        """Testa se a classe existe e se possui os métodos esperados

        Returns:
            Result: Resultado do teste
        """
        cls = getattr(self.import_info.module, self.class_name, None)
        if cls is None:
            logger.warning(f"A classe '{self.class_name}' não foi encontrada no módulo.")
            return Result(False, f"A classe '{self.class_name}' não foi encontrada")

        for method in self.methods:
            if not hasattr(cls, method["name"]):
                logger.warning(f"O método '{method['name']}' não foi encontrado na classe '{self.class_name}'.")
                return Result(False, f"O método '{method['name']}' não foi encontrada")

        return Result(True, "")

    def initialize_instance(self, *args) -> bool:
        """Inicializa uma instância da classe com os argumentos fornecidos

        Returns:
            Result: Resultado do teste
        """
        if not self.exists:
            logger.warning(f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")
            return Result(False, f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")

        cls = getattr(self.import_info.module, self.class_name, None)
        try:
            self.instance = cls(*args)
        except Exception as e:
            logger.warning(f"Falha ao inicializar a instância da classe '{self.class_name}': {e}")
            return Result(False, f"Falha ao inicializar a instância da classe '{self.class_name}'")

        return Result(True, "")

    def get_existance(self):
        """Retorna se a classe existe e possui os métodos esperados

        Returns:
            Result: Resultado do teste
        """
        return self.exists

    def test_method(self, method_name: str, static: bool, input_args: list, expected_output) -> Result:
        """Testa se um método da classe retorna o valor esperado

        Args:
            method_name (str): Nome do método
            static (bool): Se o método é estático ou não
            input_args (list): Argumentos de entrada para o método
            expected_output: Output esperado

        Returns:
            Result: O resultado do teste
        """
        test_result = Result(success=False, error="")
        if not self.exists:
            logger.warning(f"A classe '{self.class_name}' não existe ou não possui os métodos esperados.")
            return test_result

        try:
            cls = getattr(self.import_info.module, self.class_name, None)
            method = getattr(cls, method_name, None)

            if not static and self.instance is not None:
                result, captured_stdout, _ = _call_with_captured_output(method, self.instance, *input_args)
            else:
                result, captured_stdout, _ = _call_with_captured_output(method, *input_args)

            observed_output = result if result is not None else captured_stdout
            if observed_output != expected_output and str(observed_output) != str(expected_output):
                logger.warning(f"O método '{method_name}' retornou '{observed_output}', mas era esperado '{expected_output}'.")
                test_result.error = f"retornou '{observed_output}', mas era esperado '{expected_output}'."
                return test_result
        except Exception as e:
            logger.warning(f"Falha ao testar o método '{method_name}': {e}")
            logger.warning(f"Traceback: {traceback.format_exc()}")
            return test_result

        test_result.success = True
        return test_result

class FunctionTester:
    """Contempla a lógica de teste de uma função importada de um módulo Python"""
    def __init__(self, import_info: Imported, function_name: str):
        """Inicializa a instância da classe

        Args:
            import_info (Imported): Informações sobre o módulo importado
            function_name (str): Nome da função a ser testada
        """
        self.import_info = import_info
        self.function_name = function_name
        self.exists = self.check_existance()

    def check_existance(self) -> Result:
        """Testa se a função existe

        Returns:
            Result: Resultado do teste
        """
        func = getattr(self.import_info.module, self.function_name, None)
        if func is None:
            logger.warning(f"A função '{self.function_name}' não foi encontrada no módulo.")
            return Result(False, f"A função '{self.function_name}' não foi encontrada")

        return Result(True, "")

    def get_existance(self):
        """Retorna se a função existe"""
        return self.exists

    def test(self, input_args: list, expected_output) -> Result:
        """Testa se a função retorna o valor esperado

        Args:
            input_args (list): Lista de argumentos a serem passados para a função
            expected_output: Valor esperado como saída da função

        Returns:
            Result: Resultado do teste, contendo sucesso e mensagem de erro se houver
        """
        test_result = Result(success=False, error="")
        if not self.exists:
            logger.info(f"A função '{self.function_name}' não existe.")
            return test_result

        try:
            func = getattr(self.import_info.module, self.function_name, None)
            result, captured_stdout, _ = _call_with_captured_output(func, *input_args)
            observed_output = result if result is not None else captured_stdout
            if observed_output != expected_output and str(observed_output) != str(expected_output):
                logger.warning(f"A função '{self.function_name}' retornou '{observed_output}', mas era esperado '{expected_output}'.")
                test_result.error = f"retornou '{observed_output}', mas era esperado '{expected_output}'."
                return test_result
        except Exception as e:
            logger.warning(f"Falha ao testar a função '{self.function_name}': {e}")
            logger.warning(f"Traceback: {traceback.format_exc()}")
            return test_result

        test_result.success = True
        return test_result