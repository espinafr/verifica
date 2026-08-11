from colorama import Style
import re

# Regex para códigos ANSI de cores e formatação
ANSI_PATTERN = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")

class TUI:
    @staticmethod
    def visible_len(text: str) -> int:
        """Retorna o tamanho de uma string sem caracteres de formatação ANSI"""
        return len(ANSI_PATTERN.sub("", text))

    def __init__(self, contents: list, show: bool = False, max_line: int = -1, padding: int = 1):
        self.contents = contents
        self.padding = padding
        self.max_line = max_line
        self.min_size = self.__get_longest_message_length() + (padding * 2)
        self.row_size = self.min_size + self.padding
        if show:
            self.show()

    def __get_longest_message_length(self):
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
        lines = []
        paragraphs = text.split('\n')

        lines.append(f"{key}{Style.RESET_ALL} {paragraphs[0]}")
        for paragraph in paragraphs[1:]:
            lines.append(f"{' ' * (self.visible_len(key) + 1)}{paragraph}{Style.RESET_ALL}")

        return lines

    def __create_paragraphs(self, key: str, text: str) -> str:
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

    def __create_top_border(self):
        return f"╔{'═' * self.row_size}╗"

    def __create_internal_border(self):
        return f"╠{'═' * self.row_size}╣"

    def __create_bottom_border(self):
        return f"╚{'═' * self.row_size}╝"

    def __create_left_border(self):
        return f"║"

    def __create_right_border(self):
        return f"║"

    def __create_center_row(self, text: str):
        return f"{self.__create_left_border()}{" "*self.padding}{text.center(self.min_size - self.padding + (len(text) - self.visible_len(text)))}{Style.RESET_ALL}{" "*self.padding}{self.__create_right_border()}"

    def __create_row(self, text: str):
        return f"{self.__create_left_border()}{" "*self.padding}{text.ljust(self.min_size - self.padding + (len(text) - self.visible_len(text)))}{" "*self.padding}{Style.RESET_ALL}{self.__create_right_border()}"

    def show(self):
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
