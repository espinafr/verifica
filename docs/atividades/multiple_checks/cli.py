# Arquivo 2
# Solução do exercício de exemplo
# espinafr/verifica/master/docs/atividades/multiple_checks

import argparse

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("nome", action="store")
    args = parser.parse_args()
    if args.nome:
        print(f"Hello, {args.nome}!")
    else:
        print("Hello, World!")

if __name__ == "__main__":
    main()
