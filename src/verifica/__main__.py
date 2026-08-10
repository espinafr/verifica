import argparse
from pathlib import Path
from colorama import init
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
init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Uma ferramenta simples para correção de atividades em python via CLI.", add_help=False)
    positional = parser.add_argument_group("argumentos posicionais")
    options = parser.add_argument_group("opções")

    positional.add_argument("atividade", nargs="?", help="A URL do github ou caminho local do arquivo usado para a correção da atividade.")
    options.add_argument("-f", "--files", default=Path.cwd(), help="Diretório com a(s) atividade(s) a ser(em) corrigida(s).")
    options.add_argument("-h", "--help", "--ajuda", action="help", help="Mostra essa mensagem de ajuda.")
    options.add_argument("-c", "--config", action="store_true", help="Mostra o caminho do arquivo de configuração.")
    options.add_argument("-d", "--debug", action="store_true", help="Ativa o modo debug, mostrando mais informações durante a execução.")
    options.add_argument("-l", "--local", action="store_true", help="Caminho local para a pasta com o arquivo de respostas, caso não queira baixar do github.")
    
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Modo debug ativado. Mostrando informações detalhadas durante a execução.")
    
    if args.config:
        print(settings.config_path)
        return

    if not args.atividade:
        parser.error("o seguinte argumento é obrigatório: atividade")

    if not args.local:
        answers = Fetcher(args.atividade)
        try:
            print("Baixando arquivo de correção...")
            logging.debug(f"CAMINHO DO ARQUIVO BAIXADO: {answers.fetch()}")
        except Exception as e:
            logging.error(f"Não foi possível localizar o arquivo de correção em '{args.atividade}'")
            sys.exit(1)
    else:
        answers = Fetcher(args.atividade, local=True)
        try:
            print("Buscando arquivo de correção local...")
            logging.debug(f"CAMINHO DO ARQUIVO LOCAL: {answers.get_file()}")
        except Exception as e:
            logging.error(f"Não foi possível localizar o arquivo de correção em '{args.atividade}'")
            sys.exit(1)

    decoded_answers = answers.get_decoded_json()
    answers.cleanup()

    checker = Checker(args.files, decoded_answers)

    checker.setup_roadmap()

    results = checker.run_roadmap()
    checker.show_results(results)
    
    sys.exit(0)

if __name__ == "__main__":
    main()