
import radical.utils as ru

SELECT_1D       = '1D'
SELECT_TEST     = 'TEST'
EXCHANGE_RANDOM = 'RANDOM'

_log = ru.Logger('radical.repex')


# ------------------------------------------------------------------------------
#
def select_replicas_1D(waitlist, criteria, replica):
    '''
    replica selection algorithm: out of the list of eligible replicas, select
    those which should be part of an exchange step.

    Arguments:

      - waitlist: a list of replica objects which are eligible for exchange
      - criteria: dictionary of selection criteria to control the algorthm's
    '''

    try:
        _log.debug('criteria: %s' % criteria)
        _log.debug('waitlist: %s' % [r.rid for r in waitlist])

        # get required parameters
        ex_size = criteria['exchange_size']

        # check if size of wait list suffices
        if len(waitlist) < ex_size:

            # not enough replicas to attempt exchange
            return [], waitlist
        elif len(waitlist) > ex_size:
            # waitlist somehow grew too large

            raise ValueError('The waitlist is larger than maximum permissible exchange list size')

        # we have enough replicas!  Remove all as echange candidates from the
        # waitlist and return them!
        exchange_list = list()
        for r in waitlist:
            exchange_list.append(r)

        # empty the waitlist to start collecting new candidates
        new_waitlist = list()

        _log.debug('exchange: %s' % [r.rid for r in exchange_list])
        _log.debug('new wait: %s' % [r.rid for r in new_waitlist])

        return exchange_list, new_waitlist


    except Exception:

        _log.exception('replica selection failed')

        # on failure, return the unchanged waitlist and an empty selection
        return [], waitlist


# ------------------------------------------------------------------------------
#
def select_replicas_test(waitlist, criteria, replica):

    if len(waitlist) < criteria['exchange_size']:
        return [], waitlist

    return [r for r in waitlist], []


# ------------------------------------------------------------------------------
#
def exchange_by_random():
    '''
    This method is run as workload of exchange tasks.  It will receive two
    arguments: the number of replicas to exchange, and the cycle (?).
    '''

    import sys
    import random

    replicas = int(sys.argv[1])
    cycle    = int(sys.argv[2])

    exchange_list_1 = range(replicas)
    exchange_list_2 = range(replicas)

    random.shuffle(exchange_list_1)
    random.shuffle(exchange_list_2)

    exchangePairs = zip(exchange_list_2, exchange_list_2)

    with open('exchangePairs_%d.dat' % cycle, 'w') as f:
        for p in exchangePairs:
            line = ' '.join(str(x) for x in p)
            f.write(line + '\n')


# ------------------------------------------------------------------------------

