import argparse
from pathlib import Path

from config import settings
from check import Checker
from fetcher import Fetcher

def main():
    parser = argparse.ArgumentParser(description="Uma ferramenta simples para correção de atividades via CLI.", add_help=False)

    parser.add_argument("atividade", nargs="?", help="A URL do github usada para a correção da atividade.")
    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Mostra essa mensagem de ajuda.")
    parser.add_argument("-c", "--config", action="store_true", help="Mostra o caminho do arquivo de configuração.")
    parser.add_argument("-a", "-f", "--files", default=Path.cwd(), help="Diretório com a(s) atividade(s) a ser(em) corrigida(s).")
    
    args = parser.parse_args()

    if args.config:
        print(settings.config_path)
        return

    if not args.atividade:
        parser.error("o seguinte argumento é obrigatório: atividade")

    answers = Fetcher(args.atividade)
    try:
        print(answers.fetch())
    except RuntimeError:
        parser.error(f"Falha ao buscar o exercício '{args.atividade}'")
    
    checker = Checker(answers.get_decoded_json(), args.files)
    
    answers.cleanup()
    del answers

if __name__ == "__main__":
    main()