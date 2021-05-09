import random


class LexemFormatter:

    def __init__(self, lexem):
        super().__init__()
        self.lexem = lexem

    def hidden_state(self):
        res = f"{self.lexem.id}|\n"
        if random.randint(0, 1):
            res += str(self.lexem.russian)
        else:
            res += str(self.lexem.english)
        if self.lexem.context:
            res += f"\n({self.lexem.context})"
        return res

    def open_state(self):
        res = f"{self.lexem.id}|\n"
        res += str(self.lexem.russian)
        res += "\n\n - "
        res += str(self.lexem.english)
        if self.lexem.context:
            res += f"\n({self.lexem.context})"
        return res
