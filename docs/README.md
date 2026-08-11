# Arquivos de correção
Arquivos de correção são listas com os comportamentos esperados de um exercício. Eles descrevem o que a ferramenta deve verificar em arquivos Python, como saídas de CLI, funções, classes, entradas simples e entradas sequenciais.

Esses arquivos devem seguir uma estrutura JSON rígida. Qualquer desvio pode fazer a ferramenta considerar o arquivo inválido e interromper a execução.

<details>
    <summary><strong>Sumário</strong></summary>
    <ol>
        <li><a href="#nome-e-localização">Nome e localização</a></li>
        <li><a href="#estrutura-geral">Estrutura geral</a></li>
        <li><a href="#blocos-de-verificação">Blocos de verificação</a>
            <ul>
                <li><a href="#1-cli">1. CLI</a></li>
                <li><a href="#2-structure">2. STRUCTURE</a></li>
                <ul>
                    <li><a href="#functions">FUNCTIONS</a></li>
                    <li><a href="#classes">CLASSES</a></li>
                </ul>
                <li><a href="#3-inputs">3. INPUTS</a></li>
            </ul>
        </li>
        <li><a href="#regras-importantes">Regras importantes</a></li>
        <li><a href="#exemplo-completo">Exemplo completo</a></li>
    </ol>
</details>

## Nome e localização
Todo arquivo de correção deve se chamar exatamente "`correcao.json`" e deve **ser o único arquivo com esse nome** dentro da pasta do exercício. 

Por padrão, a ferramenta vai procurar arquivos em https://raw.githubusercontent.com/ usando o esquema `usuario/repositorio/branch/localizacao/da/pasta`

Para usar arquivos de correção locais basta executar a ferramenta com a flag  `-l` seguida do caminho do arquivo.
```bash
verifica -l C:\Users\user\Desktop\atividade_input
```

Precisa de uma ajuda fazendo seu `correcao.json`? Use o próprio gerador da ferramenta!
```
verifica --builder
```

## Estrutura geral
Um arquivo de correção é um JSON com três chaves principais:

- `files`: lista dos arquivos que serão avaliados
- `description`: descrição do exercício _(opcional)_
- para cada nome de arquivo listado em `files`, uma chave contendo as verificações daquele arquivo

Exemplo mínimo:

```json
{
    "files": ["arquivo.py"],
    "description": "Exercício de exemplo",
    "arquivo.py": {
        "CLI": []
    }
}
```

## Blocos de verificação
Cada arquivo listado em "files" pode conter um ou mais blocos de testes. Os blocos aceitos pelo projeto são:

### 1. CLI
Usado para testar comandos executados no terminal.

Cada item da lista deve ter:

- `input`: texto de entrada, separado por espaço para simular argumentos de linha de comando
- `expected`: texto esperado na saída do programa
- `info`: descrição opcional da verificação

Exemplo:

```json
"arquivo.py": {
    "CLI": [
    {
        "input": "",
        "expected": "Hello, World!",
        "info": "mostra hello world no console"
        }
    ]
}
```

> A comparação é feita verificando se o texto esperado aparece na saída produzida pelo programa.

### 2. STRUCTURE
Usado para verificar a existência e o comportamento de funções e classes.

Esse bloco possui duas chaves internas:

- `FUNCTIONS`: lista de funções esperadas
- `CLASSES`: lista de classes esperadas

#### Funções
Cada função precisa ter:

- `name`: nome da função
- `runs`: lista de testes para essa função

Cada item de `runs` deve ter:

- `input`: lista de argumentos usados na chamada
- `expected`: valor esperado retornado
- `info`: descrição opcional

Exemplo:

```json
"arquivo.py": {
    "STRUCTURE": {
        "FUNCTIONS": [
            {
                "name": "soma",
                "runs": [
                    {
                        "input": [1, 2],
                        "expected": "3"
                    }
                ]
            }
        ]
    }
}
```

#### Classes
Cada classe precisa ter:

- `name`: nome da classe
- `initialized`: booleano indicando se a classe deve ser instanciada
- `initializer`: objeto com `input` e `info` opcional, usado quando `initialized` for true
- `methods`: lista opcional dos métodos esperados

Cada método deve ter:

- `name`: nome do método
- `input`: lista de argumentos do método
- `expected`: valor esperado retornado
- `info`: descrição opcional
- `static`: booleano opcional, indicando se o método é estático

Exemplo:

```json
"arquivo.py": {
    "STRUCTURE": {
        "CLASSES": [
            {
                "name": "Pessoa",
                "initialized": true,
                "initializer": {
                    "input": ["Théo", 18]
                },
                "methods": [
                    {
                        "name": "aniversario",
                        "input": [1],
                        "expected": "19"
                    }
                ]
            }
        ]
    }
}
```

### 3. INPUTS
Usado para testar a leitura de entrada pelo programa. Os valores esperados e input podem ser strings ou listas no caso de múltipls inputs e saídas.

Cada item deve ter:

- `input`: texto enviado ao programa via stdin (lista ou string)
- `expected`: saída esperada (lista ou string)
- `info`: descrição opcional

Exemplos:

```json
"arquivo.py": {
    "INPUTS": [
        {
            "input": "Théo",
            "expected": "Olá Théo"
        }
    ]
}
```

```json
"arquivo.py": {
    "INPUTS": [
    {
        "input": ["amora", "morango", "cereja"],
        "expected": ["Hmmm, também gosto de amora, morango e cereja!"]
        }
    ]
}
```

## Regras importantes
- Os nomes das chaves devem ser exatamente como acima: `files`, `description`, `CLI`, `STRUCTURE`, `FUNCTIONS`, `CLASSES` e `INPUTS`
- A estrutura do JSON deve respeitar a ordem esperada pelo validador do projeto.
- Cada arquivo listado em `files` deve ter pelo menos um bloco de verificação.
- Os campos `input` e `expected` são obrigatórios nos itens de teste e `info` é opcional.
- O valor esperado é comparado como parte da saída produzida, não necessariamente como uma igualdade exata.

## Exemplo completo
Um arquivo de correção pode combinar vários tipos de teste em um mesmo exercício:

```json
{
  "files": ["classes.py", "cli.py"],
  "description": "Exercício com múltiplos arquivos e testes",
  "classes.py": {
    "STRUCTURE": {
      "FUNCTIONS": [
        {
          "name": "soma",
          "runs": [
            {
              "input": [1, 2],
              "expected": "3"
            }
          ]
        }
      ],
      "CLASSES": [
        {
          "name": "Pessoa",
          "initialized": true,
          "initializer": {
            "args": ["Théo", 18]
          },
          "methods": [
            {
              "name": "aniversario",
              "input": [1],
              "expected": "19"
            }
          ]
        }
      ]
    }
  },
  "cli.py": {
    "CLI": [
      {
        "input": "",
        "expected": "Hello, World!"
      }
    ]
  }
}
```