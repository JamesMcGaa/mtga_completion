from constants import CARDS_PER_RARITY
import random


class mtg_set:
    def __init__(
        self,
        expansion,
        preexisting=None,
        vault_progress=0,
        wildcards=None,
        pack_wildcard_bonuses=None,
    ):
        self.rarity_distribution = expansion["rarity_distribution"]
        self.mythic_rate = expansion["mythic_rate"]

        if preexisting == None:
            # rarity C,U,R,M to a list of counts in range [0,4]
            self.preexisting = list(
                map(lambda x: [0 for _ in range(x)], expansion["rarity_distribution"])
            )

        self.vault_progress = vault_progress

        if wildcards == None:
            self.wildcards = [0, 0, 0, 0]

        if pack_wildcard_bonuses == None:  # U, R, M
            self.pack_wildcard_bonuses = [0, 0, 0]

        self.gems = 0
        self.packs_purchased = 0
        self.packs_opened = 0
        self.wildcard_misses = [0, 0, 0, 0]
        self.pity_limits = [5, 5, 15, 30]
        self.wildcard_rates = [1 / 3, 1 / 5, 1 / 30, 1 / 30]

    def is_completed(self):
        for rarity_index in range(4):
            if self.count_missing_at_rarity(rarity_index) != 0:
                return False
        return True

    def complete_set(self):
        while not self.is_completed():
            if self.gems >= 200:
                self.gems -= 200
            else:
                self.packs_purchased += 1
            self.add_pack()

        return self.packs_purchased

    def add_pack(self):
        self.packs_opened += 1
        self.increment_pack_guaranteed_wildcards()

        # mythic or rare
        rarity_indices = [0, 1, 2 if random.random() > self.mythic_rate else 3]

        for rarity_index in rarity_indices:
            self.add_cards_per_rarity(rarity_index)

        self.vault_and_wildcard_checks()

    def increment_pack_guaranteed_wildcards(self):
        for pack_wildcard_bonus_index in range(3):
            self.pack_wildcard_bonuses[pack_wildcard_bonus_index] += 1

        # uncommon
        if self.pack_wildcard_bonuses[0] == 6:
            self.wildcards[1] += 1
            self.pack_wildcard_bonuses[0] = 0

        # mythic
        if self.pack_wildcard_bonuses[2] == 24:
            self.wildcards[3] += 1
            self.pack_wildcard_bonuses[2] = 0
            self.pack_wildcard_bonuses[1] = 0

        # rare
        if self.pack_wildcard_bonuses[1] == 6:
            self.wildcards[2] += 1
            self.pack_wildcard_bonuses[1] = 0

    def add_cards_per_rarity(self, rarity_index):
        self.wildcard_misses[rarity_index] += 1

        num_nonwildcards_to_open = CARDS_PER_RARITY[rarity_index]

        if (  # wildcard
            self.pity_limits[rarity_index] == self.wildcard_misses[rarity_index]
            or random.random() < self.wildcard_rates[rarity_index]
        ):
            self.pity_limits[rarity_index] = 0
            self.wildcards[rarity_index] += 1
            num_nonwildcards_to_open -= 1

        if rarity_index in [0, 1]:
            drawn_unique_cards = random.sample(
                [index for index in range(self.rarity_distribution[rarity_index])],
                num_nonwildcards_to_open,
            )
            for index in drawn_unique_cards:
                if self.preexisting[rarity_index][index] == 4:
                    self.process_surplus_rarity(rarity_index)
                else:
                    self.preexisting[rarity_index][index] += 1

        else:
            all_indices = [x for x in range(self.rarity_distribution[rarity_index])]
            non_complete = list(
                filter(
                    lambda index: self.preexisting[rarity_index][index] != 4,
                    all_indices,
                )
            )
            if len(non_complete) == 0:
                self.process_surplus_rarity(rarity_index)
                return
            drawn_rare_type_card = random.choice(non_complete)
            self.preexisting[rarity_index][drawn_rare_type_card] += 1

    def count_missing_at_rarity(self, rarity_index):
        return 4 * self.rarity_distribution[rarity_index] - sum(
            self.preexisting[rarity_index]
        )

    def process_surplus_rarity(self, rarity_index):
        if rarity_index == 0:
            self.vault_progress += 1
        elif rarity_index == 1:
            self.vault_progress += 3
        elif rarity_index == 2:
            self.gems += 20
        elif rarity_index == 3:
            self.gems += 40
        else:
            raise IndexError("Improper rarity passed to process_surplus_rarity")

    def vault_and_wildcard_checks(self):
        if self.vault_progress >= 1000:
            self.vault_progress -= 1000
            self.wildcards[1] += 3
            self.wildcards[2] += 2
            self.wildcards[3] += 1

        for rarity_index in range(4):
            if self.wildcards[rarity_index] > 0:
                missing_at_rarity = self.count_missing_at_rarity(rarity_index)

                # convert excess to gems or vault
                if missing_at_rarity == 0:
                    for _ in range(self.wildcards[rarity_index]):
                        self.process_surplus_rarity(rarity_index)
                    self.wildcards[rarity_index] = 0

                    # might have gone over vault threshhold, so check again
                    self.vault_and_wildcard_checks()

                # complete set at rarity
                elif missing_at_rarity <= self.wildcards[rarity_index]:
                    self.wildcards[rarity_index] -= missing_at_rarity
                    self.preexisting[rarity_index] = [
                        4 for _ in range(self.rarity_distribution[rarity_index])
                    ]

                    # might have gone over vault threshhold, so check again
                    self.vault_and_wildcard_checks()
