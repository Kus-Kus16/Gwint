from src.model.cards.raw_commander import RawCommander


class Commander(RawCommander):
    def __init__(self, data):
        super().__init__(data)
        self.nickname = data['nickname']
        self.active = True

    def disable(self):
        self.active = False

    def enable(self):
        self.active = True

    def ability(self):
        return self.abilities[0]