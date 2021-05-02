import random


class LexemFormatter:

    def __init__(self, lexem):
        super().__init__()
        self.lexem = lexem

    def hidden_state(self):
        res = f"{self.lexem.id}| "
        if random.randint(0, 1):
            res += str(self.lexem.russian)
        else:
            res += str(self.lexem.english)
        res += f"\n({self.lexem.context})"
        return res

    def open_state(self):
        res = f"{self.lexem.id}| "
        res += str(self.lexem.russian)
        res += " - "
        res += str(self.lexem.english)
        res += f"\n({self.lexem.context})"
        return res
