# Solução do exercício de exemplo
# espinafr/verifica/master/docs/atividades/regex_cli

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("produto")
    parser.add_argument("codigo")
    args = parser.parse_args()
    print(f"Produto: {args.produto} | codigo: {args.codigo}")


if __name__ == "__main__":
    main()
