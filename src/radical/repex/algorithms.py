
import radical.utils as ru


# ------------------------------------------------------------------------------
#
exchange_alg_prefix = '''
#!/usr/bin/env python

import sys


# ------------------------------------------------------------------------------
#
# exchange algorithm
#
%s


# ------------------------------------------------------------------------------
#
# exchange algorithm call context
#
if __name__ == '__main__':

    rid     = None
    cycle   = None
    ex_list = list()
    ex_data = list()

    arg_mode = None
    for arg in sys.argv[1:]:
        if   arg == '-r': arg_mode = 'rid'
        elif arg == '-c': arg_mode = 'cycle'
        elif arg == '-e': arg_mode = 'ex_list'
        elif arg == '-d': arg_mode = 'ex_data'
        else:
            if   arg_mode == 'rid'    : rid   = arg
            elif arg_mode == 'cycle'  : cycle = int(arg)
            elif arg_mode == 'ex_list': ex_list.append(arg)
            elif arg_mode == 'ex_data': ex_data.append(arg)

    # call the exchange algorithm inserted above
    %s(rid, cycle, ex_list, ex_data)


# ------------------------------------------------------------------------------

'''


# ------------------------------------------------------------------------------

