import subprocess
import traceback
import sys
import re

from .shared import Result, logger

# Código para, em termos simples, ""executar input() sem texto"" 
_INPUT_RUNNER = """
import builtins
import runpy
import sys


def input_without_prompt(prompt=""):
    line = sys.stdin.readline()
    if line == "":
        raise EOFError
    return line.rstrip("\\r\\n")


builtins.input = input_without_prompt
sys.argv = [sys.argv[1]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def test_INPUTS(file_path: str, input_data: list[str], expected_output: list[str], use_regex: bool = False) -> Result:
        """Testa uma sequência de inputs

        Args:
            file_path (str): Caminho do arquivo a ser testado
            input_data (list[str]): Lista de inputs a serem fornecidos ao programa
            expected_output (list[str]): Lista de saídas esperadas

        Returns:
            Result: Resultado do teste
        """
        try:
            process = subprocess.run(
                [sys.executable, "-c", _INPUT_RUNNER, file_path],
                input="\n".join(input_data) + "\n",
                capture_output=True,
                text=True
            )

            if process.returncode != 0:
                logger.warning(
                    f"[INPUT] O programa terminou com código {process.returncode}"
                )
                logger.warning(f"[INPUT] stderr: {process.stderr}")
                return Result(False, "")

            output = process.stdout.strip()
            logger.debug(f"[INPUT] Saída do input: {output}")

            if use_regex:
                output_lines = output.split('\n')
                # Remove linhas vazias no final para evitar problemas de comparação
                while output_lines and output_lines[-1] == '':
                    output_lines.pop()

                # Se há múltiplos regexes, verifica linha por linha
                if len(expected_output) > 1:
                    if len(output_lines) != len(expected_output):
                        error_msg = f"número de linhas de saída ({len(output_lines)}) não corresponde ao número de padrões esperados ({len(expected_output)})"
                        return Result(False, error_msg)

                    for i, (output_line, pattern) in enumerate(zip(output_lines, expected_output)):
                        if re.fullmatch(pattern, output_line, re.DOTALL) is None:
                            return Result(False, f"linha {i + 1}: '{output_line}' não correspondeu ao regex esperado '{pattern}'")

                    return Result(True, "")
                else:
                    # Mas um único regex pode ser multi-linha
                    expected_pattern = expected_output[0]
                    is_expected = re.fullmatch(expected_pattern, output, re.DOTALL) is not None
                    return Result(is_expected, "" if is_expected else f"o regex de output esperado '{expected_pattern}' não correspondeu à saída '{output}'")
            else:
                is_expected = all(
                    expected in output
                    for expected in expected_output
                )
                return Result(is_expected, "" if is_expected else f"o output esperado '{', '.join(expected_output)}' não correspondeu à saída '{output}'")

        except Exception as e:
            logger.warning(f"[INPUT] Falha ao executar o input '{input_data}': {e}")
            logger.warning(f"Traceback: {traceback.format_exc()}")
            return Result(False, "")