from colorama import init
from pathlib import Path
import argparse
import logging
import sys

from .config import settings

file_handler = logging.FileHandler(Path(settings.config_dir) / "app.log", mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s',
    handlers=[
        file_handler,
        console_handler
    ]
)
init(autoreset=True)

from .checker.checker import Checker
from .fetcher import Fetcher
from .builder.builder import Builder

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
    options.add_argument("--version", action="version", version=f"{settings.get_version()}", help="Mostra a versão do programa.")
    options.add_argument("-b", "--builder", action="store_true", help="TUI para criar arquivos de correção de atividades.")  

    args = parser.parse_args()

    if args.debug:
        console_handler.setLevel(logging.DEBUG)
        logging.info(f"Modo debug ativado. Mostrando informações detalhadas durante a execução. Registro de debug: {Path(settings.config_dir) / 'app.log'}")
    
    if args.config:
        print(settings.config_path)
        sys.exit(0)

    if args.builder:
        builder = Builder()
        builder.start()
        sys.exit(0)

    if not args.atividade:
        parser.error("o seguinte argumento é obrigatório: atividade")

    if not args.local:
        answers = Fetcher(args.atividade)
        try:
            print("Baixando arquivo de correção...")
            logging.debug(f"CAMINHO DO ARQUIVO BAIXADO: {answers.fetch()}")
        except Exception as e:
            logging.error(f"Não foi possível localizar o arquivo de correção em '{args.atividade}'")
            sys.exit(2)
    else:
        answers = Fetcher(args.atividade, local=True)
        try:
            print("Buscando arquivo de correção local...")
            logging.debug(f"CAMINHO DO ARQUIVO LOCAL: {answers.get_file()}")
        except Exception as e:
            logging.error(f"Não foi possível localizar o arquivo de correção em '{args.atividade}'")
            sys.exit(2)

    try:
        logging.info(f"Iniciando conversão do arquivo de correção para JSON...")
        decoded_answers = answers.get_decoded_json()
    except Exception as _: # Já tratado dentro de decoded_json
        sys.exit(2)

    answers.cleanup()

    checker = Checker(args.files, decoded_answers)

    checker.setup_roadmap()

    all_passed, results = checker.run_roadmap()
    checker.show_results(results)
    
    sys.exit(all_passed)

main()