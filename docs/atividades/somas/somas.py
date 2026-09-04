# Solução do exercício de exemplo
# espinafr/verifica/master/docs/atividades/somas

numeros = []
while (numero := input("Digite um número (ou apenas aperte enter para parar): ")) != "":
    numeros.append(int(numero))

print(sum(numeros))