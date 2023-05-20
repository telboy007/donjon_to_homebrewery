"""Module providing summary helper functions"""


def calculate_total_and_shared_xp(xp_list, party_size):
    total_xp = sum(int(i) for i in xp_list)
    shared_xp = round(sum(int(i) for i in xp_list)/int(party_size))

    return total_xp, shared_xp