class Quest:
    @staticmethod
    def reset():
        Quest.has_sword = False
        Quest.has_shield = False
        Quest.has_crown = False
        Quest.treasure_dropped_this_level = False  # only allow one treasure to drop per level

    @staticmethod
    def num_found():
        return int(Quest.has_sword) + int(Quest.has_shield) + int(Quest.has_crown)

    @staticmethod
    def can_escape():
        return Quest.has_sword and Quest.has_shield and Quest.has_crown