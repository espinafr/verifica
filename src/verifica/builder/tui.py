from colorama import Style
import re

# Regex para códigos ANSI de cores e formatação
ANSI_PATTERN = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")

class TUI:
    @staticmethod
    def visible_len(text: str) -> int:
        """Retorna o tamanho de uma string sem caracteres de formatação ANSI"""
        return len(ANSI_PATTERN.sub("", text))

    def __init__(self, contents: list[dict | str], show: bool = False, max_line: int = -1, padding: int = 1):
        """Inicializa a instância da classe

        Args:
            contents (list[dict  |  str]): Lista de dicionários e strings representando o conteúdo a ser exibido
            show (bool, optional): Se True, exibe o conteúdo imediatamente. O padrão é False.
            max_line (int, optional): Tamanho máximo de caracteres por linha. O padrão é -1.
            padding (int, optional): Espaçamento ao redor do conteúdo. O padrão é 1.
        """
        self.contents = contents
        self.padding = padding
        self.max_line = max_line
        self.min_size = self.__get_longest_message_length() + (padding * 2)
        self.row_size = self.min_size + self.padding
        if show:
            self.show()

    def __get_longest_message_length(self) -> int:
        """Obtém o número de caracteres do texto mais longo dentro do conteúdo passado à classe

        Returns:
            int: Tamanho do texto
        """
        longest = 0
        for block in self.contents:
            if isinstance(block, dict):
                for k, v in block.items():
                    for line in self.__get_paragraphs(k, self.__create_paragraphs(k, v)):
                        length = self.visible_len(line)
                        if length > longest:
                            longest = length
            else:
                length = self.visible_len(block)
                if length > longest:
                    longest = length
        return longest

    def __get_paragraphs(self, key: str, text: str) -> list:
        """Formata um texto em parágrafos, adicionando a chave do bloco de informações na primeira linha e alinhando as linhas subsequentes

        Args:
            key (str): Chave do bloco de informações
            text (str): Texto do bloco de informações

        Returns:
            list: Lista de parágrafos formatados
        """
        lines = []
        paragraphs = text.split('\n')

        lines.append(f"{key}{Style.RESET_ALL} {paragraphs[0]}")
        for paragraph in paragraphs[1:]:
            lines.append(f"{' ' * (self.visible_len(key) + 1)}{paragraph}{Style.RESET_ALL}")

        return lines

    def __create_paragraphs(self, key: str, text: str) -> str:
        """Separa parágrafos em um texto de um bloco de informações com base no tamanho máximo de caracteres por linha

        Args:
            key (str): Chave do bloco de informações
            text (str): Texto do bloco de informações

        Returns:
            str: Texto com parágrafos separados
        """
        if self.max_line >= 1:
            paragraphs = []
            unformatted_paragraphs = text.split('\n')

            for paragraph in unformatted_paragraphs:
                words = paragraph.split()
                current_line = ""
                for word in words:
                    if self.visible_len(f"{key} {current_line}") + self.visible_len(word) + 1 <= self.max_line:
                        current_line += f"{word} "
                    else:
                        paragraphs.append(current_line.strip())
                        current_line = f"{word} "

                if current_line:
                    paragraphs.append(current_line.strip())

            return '\n'.join(paragraphs)
        return [text]


    def __create_top_border(self) -> str:
        """Cria a borda superior baseada no tamanho da linha

        Returns:
            str: Borda superior
        """
        return f"╔{'═' * self.row_size}╗"


    def __create_internal_border(self) -> str:
        """Cria uma borda interior baseada no tamanho da linha

        Returns:
            str: Borda interior
        """
        return f"╠{'═' * self.row_size}╣"


    def __create_bottom_border(self) -> str:
        """Cria a borda inferior baseada no tamanho da linha

        Returns:
            str: Borda inferior
        """
        return f"╚{'═' * self.row_size}╝"


    def __create_vertical_border(self) -> str:
        """Retorna o caractere de borda vertical

        Returns:
            str: Caractere
        """
        return f"║"


    def __create_center_row(self, text: str):
        """Cria uma texto centralizado com base no tamanho da linha

        Args:
            text (str): Texto a ser centralizado

        Returns:
            _type_: Texto centralizado em linha centralizada com bordas verticais
        """
        return f"{self.__create_vertical_border()}{' '*self.padding}{text.center(self.min_size - self.padding + (len(text) - self.visible_len(text)))}{Style.RESET_ALL}{' '*self.padding}{self.__create_vertical_border()}"


    def __create_row(self, text: str):
        """Cria uma texto alinhado à esquerda com base no tamanho da linha

        Args:
            text (str): Texto a ser alinhado

        Returns:
            _type_: Texto alinhado à esquerda em linha com bordas verticais
        """
        return f"{self.__create_vertical_border()}{' '*self.padding}{text.ljust(self.min_size - self.padding + (len(text) - self.visible_len(text)))}{' '*self.padding}{Style.RESET_ALL}{self.__create_vertical_border()}"


    def show(self):
        """Exibe o conteúdo formatado na tela"""
        last_element = len(self.contents) - 1
        
        print(f"{self.__create_top_border()}")
        for index, block in enumerate(self.contents):
            if isinstance(block, dict):
                for key, message in self.contents[index].items():
                    for line in self.__get_paragraphs(key, self.__create_paragraphs(key, message)):
                        print(f"{self.__create_row(line)}")
            else:
                print(f"{self.__create_center_row(block)}")
                
            if index != last_element:
                print(f"{self.__create_internal_border()}")
            else:
                print(f"{self.__create_bottom_border()}")
