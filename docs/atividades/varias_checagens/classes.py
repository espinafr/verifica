# Arquivo 1
# Solução do exercício de exemplo
# espinafr/verifica/master/docs/atividades/varias_checagens

from datetime import datetime

class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade
        
    def aniversario(self, anos):
        self.idade += anos
        print(self.idade)

    @staticmethod
    def ano():
        print(datetime.now().year)

def soma(num1, num2):
    print(num1, num2)
    return num1 + num2

def main():
    nome = input("Digite seu nome:")
    print(f"Olá, {nome}!")

if __name__ == "__main__":
    main()