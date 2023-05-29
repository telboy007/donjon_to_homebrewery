"""Module providing summary helper functions"""


def calculate_total_and_shared_xp(xp_list, party_size):
    """ calculate total and shared xp based on combat and party size"""
    total_xp = sum(int(i) for i in xp_list)
    shared_xp = round(sum(int(i) for i in xp_list)/int(party_size))

    return total_xp, shared_xp


def dedupe_and_sort_list_via_dict(input_list):
    """ dedupes and sorts list using dict """
    output_list = list(dict.fromkeys(input_list))
    output_list.sort()

    return output_list
