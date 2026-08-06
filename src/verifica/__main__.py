import argparse
from pathlib import Path

from config import settings
from check import Checker

def main():
    parser = argparse.ArgumentParser(description="Uma ferramenta simples para correção de atividades via CLI.", add_help=False)

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Mostra essa mensagem de ajuda.")
    parser.add_argument("-c", "--caminho", default=Path.cwd(), help="O caminho do arquivo para correção.")
    parser.add_argument("atividade", help="O caminho do github usado para a correção da atividade.")
    
    args = parser.parse_args()
    
    checker = Checker(args.atividade, args.caminho)

if __name__ == "__main__":
    main()