# Solução do exercício de exemplo
# espinafr/verifica/refs/heads/master/docs/atividades/classes

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