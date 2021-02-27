class Quest:
    has_sword = False
    has_shield = False
    has_crown = False

    @staticmethod
    def can_escape():
        return Quest.has_sword and Quest.has_shield and Quest.has_crown