class Value:
    def __init__(self, name, comment):
        self.name = name  # Название item
        self.comment = comment

    def to_dict(self):
        return {
            "name": self.name,
            "comment": self.comment,
        }

    def __repr__(self):
        return f"Item(name={self.name}, comment={self.comment})"

class Item:
    def __init__(self, name, comment, values=None):
        self.name = name  # Название item
        self.values = values if values else []  # Массив строк
        self.comment = comment

    def to_dict(self):
        return {
            "name": self.name,
            "values": [value.to_dict() for value in self.values] if self.values else None,
            "comment": self.comment,
        }

    def __repr__(self):
        return f"Item(name={self.name}, comment={self.comment}, values={self.values})"


class Title:
    def __init__(self, name, comment, values=None):
        self.name = name  # Название title
        self.values = values if values else []
        self.comment = comment

    def to_dict(self):
        return {
            "name": self.name,
            "values": [value.to_dict() for value in self.values] if self.values else None,
            "comment": self.comment,
        }

    def __repr__(self):
        return f"Title(name={self.name}, comment={self.comment}, values={self.values})"


class Block:
    def __init__(self, name, recommendation, norecommendation, items=None, titles=None):
        self.name = name  # Название блока
        self.recommendation = recommendation  # Комментарий блока
        self.norecommendation = norecommendation

        self.items = items if items else []  # Список объектов Item
        self.titles = titles if titles else []  # Список объектов Title

    def to_dict(self):
        return {
            "name": self.name,
            "recommendation": self.recommendation,
            "norecommendation": self.norecommendation,
            "items": [item.to_dict() for item in self.items] if self.items else None,
            "titles": [title.to_dict() for title in self.titles] if self.titles else None
        }

    def __repr__(self):
        return f"Block(name={self.name}, recommendation={self.recommendation}, norecommendation={self.norecommendation}, items={self.items}, titles={self.titles})"


class Diagnosis:
    def __init__(self, name, code):
        self.name = name  # Название диагноза
        self.code = code
        self.blocks = []  # Список блоков в диагнозе

    def add_block(self, block):
        self.blocks.append(block)  # Добавляем блок в диагноз

    def to_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "blocks": [block.to_dict() for block in self.blocks]
        }

    def __repr__(self):
        return f"Diagnosis(name={self.name}, code={self.code}, blocks={self.blocks})"


class Section:
    def __init__(self, name):
        self.name = name  # Название секции
        self.diagnoses = []  # Список диагнозов в секции

    def add_diagnosis(self, diagnosis):
        self.diagnoses.append(diagnosis)  # Добавляем диагноз в секцию

    def to_dict(self):
        return {
            "name": self.name,
            "diagnoses": [diagnosis.to_dict() for diagnosis in self.diagnoses]
        }

    def __repr__(self):
        return f"Section(name={self.name}, diagnoses={self.diagnoses})"
