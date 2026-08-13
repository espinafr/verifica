import subprocess
import sys

from .shared import Result, logger

def test_CLI(file_path: str, input_args: list[str], expected_output: str) -> Result:
    """Testa um comando CLI de um programa Python

    Args:
        file_path (str): Caminho do arquivo a ser testado
        input_data (list[str]): Lista de inputs a serem fornecidos ao programa
        expected_output (str): Saída esperada

    Returns:
        Result: Resultado do teste
    """
    try:
        process = subprocess.run(
            [sys.executable, file_path] + input_args, 
            capture_output=True, 
            text=True
        )

        if process.returncode != 0:
            logger.warning(
                f"[CLI] O programa terminou com código {process.returncode}"
            )
            logger.warning(f"[CLI] stderr: {process.stderr}")
            return Result(False, "")

        output = process.stdout.strip()
        logger.debug(f"[CLI] Saída do comando '{' '.join(input_args)}': {output}")

        is_expected = expected_output in output
        return Result(is_expected, "" if is_expected else f"retornou '{output}', mas era esperado '{expected_output}'")

    except Exception as e:
        logger.warning(
            f"[CLI] Falha ao executar o comando '{file_path} {' '.join(input_args)}': {e}"
        )
        return Result(False, "")