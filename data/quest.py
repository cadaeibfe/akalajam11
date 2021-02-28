class Quest:
    @staticmethod
    def reset():
        Quest.has_sword = False
        Quest.has_shield = False
        Quest.has_crown = False
        Quest.min_kills_until_treasure = 5  # stop treasures from dropping twice in a row
        Quest.reset_kills()

    @staticmethod
    def num_found():
        return int(Quest.has_sword) + int(Quest.has_shield) + int(Quest.has_crown)

    @staticmethod
    def can_escape():
        return Quest.has_sword and Quest.has_shield and Quest.has_crown

    @staticmethod
    def can_drop_treasure():
        return Quest.kills_until_treasure <= 0

    @staticmethod
    def reset_kills():
        Quest.kills_until_treasure = Quest.min_kills_until_treasure