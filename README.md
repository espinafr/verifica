<div align="center">
    <h1 align="center">Verifica</h1>
    <p align="center">Uma ferramenta simples para correção de atividades em python via CLI.</p>
</div>

## Sobre o projeto

**Verifica** é uma ferramenta simples que permite que professores preparem testes automatizados para corrigir suas ativiaddes em python, fornecendo aos alunos uma correção instantânea para seus programas antes deles serem enviados.

## Como compilar

Para gerar os arquivos de distribuição do projeto, certifique-se de ter o módulo `build` instalado:

```bash
pip install build
```

Em seguida, execute o comando de construção na raiz do projeto:

```bash
python -m build
```

Os arquivos gerados (arquivos `.tar.gz` e `.whl`) estarão disponíveis no diretório `dist/`. Use o arquivo `.whl` para distribuição e instalação do pacote via pip.

```bash
pip install dist/{NOME DO ARQUIVO GERADO}
```

## Licença

Veja o arquivo LICENSE.