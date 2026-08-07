import argparse
from pathlib import Path
import logging
import sys

from .config import settings
from .check import Checker
from .fetcher import Fetcher

logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(message)s',
    handlers=[logging.FileHandler(f'{settings.config_dir}/app.log', mode='w', encoding='utf-8'), logging.StreamHandler(stream=sys.stdout)]
)

def main():
    parser = argparse.ArgumentParser(description="Uma ferramenta simples para correção de atividades em python via CLI.", add_help=False)

    parser.add_argument("atividade", nargs="?", help="A URL do github usada para a correção da atividade.")
    parser.add_argument("-a", "-f", "--files", default=Path.cwd(), help="Diretório com a(s) atividade(s) a ser(em) corrigida(s).")
    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Mostra essa mensagem de ajuda.")
    parser.add_argument("-c", "--config", action="store_true", help="Mostra o caminho do arquivo de configuração.")
    parser.add_argument("-d", "--debug", action="store_true", help="Ativa o modo debug, mostrando mais informações durante a execução.")
    
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Modo debug ativado. Mostrando informações detalhadas durante a execução.")
    
    if args.config:
        print(settings.config_path)
        return

    if not args.atividade:
        parser.error("o seguinte argumento é obrigatório: atividade")

    answers = Fetcher(args.atividade)
    try:
        logging.debug(f"CAMINHO DO ARQUIVO BAIXADO: {answers.fetch()}")
    except RuntimeError as e:
        parser.error(f"Não foi possível buscar o exercício '{args.atividade}'")

    decoded_answers = answers.get_decoded_json()
    answers.cleanup()

    checker = Checker(args.files, decoded_answers)

    try:
        checker.setup_roadmap()
    except ValueError as e:
        parser.error(f"Erro ao configurar o roadmap: {e}")

    results = checker.run_roadmap()
    checker.show_results(results)

if __name__ == "__main__":
    main()