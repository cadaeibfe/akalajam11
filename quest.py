class Quest:
    @staticmethod
    def reset():
        Quest.has_sword = False
        Quest.has_shield = False
        Quest.has_crown = False

    @staticmethod
    def can_escape():
        return Quest.has_sword and Quest.has_shield and Quest.has_crown