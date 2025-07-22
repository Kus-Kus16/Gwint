from src.model.cards.raw_commander import RawCommander


class CommanderEntry(RawCommander):
    def __init__(self, data):
        super().__init__(data)

    def dump(self):
        return self.id