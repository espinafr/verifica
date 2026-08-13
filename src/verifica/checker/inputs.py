import subprocess
import traceback
import sys

from .shared import Result, logger

def test_INPUTS(file_path: str, input_data: list[str], expected_output: list[str]) -> Result:
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
                [sys.executable, file_path],
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

            is_expected = all(
                expected in output
                for expected in expected_output
            )

            return Result(is_expected, "" if is_expected else f"o output esperado '{', '.join(expected_output)}' não foi encontrado em '{output}'")

        except Exception as e:
            logger.warning(f"[INPUT] Falha ao executar o input '{input_data}': {e}")
            logger.warning(f"Traceback: {traceback.format_exc()}")
            return Result(False, "")