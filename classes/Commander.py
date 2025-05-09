from classes.Card import CardType


class Commander:
    def __init__(self, data, faction):
        self.id = data['id']
        self.name = data['name']
        self.faction = faction
        self.owner = None
        self.nickname = data['nickname']
        self.type = CardType.COMMANDER
        self.active = True
        self.ability = data['ability']
        self.filename = data['filename']

    def is_commander(self):
        return self.type == CardType.COMMANDER