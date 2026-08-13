# Solução do exercício de exemplo
# espinafr/verifica/master/docs/atividades/varios_inputs

answers = []
for i in range(3):
    answer = input(f"[{i + 1}/3] Fale uma coisa que você gosta: ")
    answers.append(answer)

if answers[0] != "REPITA":
    print(f"Hmmm, também gosto de {answers[0]}, {answers[1]} e {answers[2]}!")
else:
    for i in range(1, 3):
        print(answers[i])