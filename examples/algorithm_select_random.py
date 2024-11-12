#!/usr/bin/env python3

import random


# ------------------------------------------------------------------------------
#
def select_by_random(waitlist, selection, replica):
    '''
    once `criteria[exchange_size]` replicas are waiting, a random subset smaller
    to equal of that size is selected for exchange.
    '''

    # check if size of wait list suffices
    if len(waitlist) < criteria.exchange_size:
        return [], waitlist

    # we have enough replicas.  Consider all to be exchange candidates and
    # select a subset (try until the active replica is included)
    while True:
        ret = random.sample(waitlist, criteria.exchange_size)
        if replica in ret:
            break

    # the new waitlist is the waitlist minus replicas selected for exchange
    new_waitlist = [r for r     in waitlist
                      if  r not in ret]

    # ret is the list of replicas  eligible for exchange
    # new_waitlist lists those not eligible for exchange
    return ret, new_waitlist


# ------------------------------------------------------------------------------

