
import copy

import time
import inspect

import threading as mt

import radical.entk  as re
import radical.utils as ru

from . import algorithms as rxa


_sel_algs = {
             rxa.SELECT_1D   : rxa.select_replicas_1D,
             rxa.SELECT_TEST : rxa.select_replicas_test
            }

_exc_algs = {
             rxa.EXCHANGE_RANDOM : rxa.exchange_by_random
            }


# ------------------------------------------------------------------------------
#
class Exchange(re.AppManager):

    _t_0    = time.time()
    _glyphs = {re.states.INITIAL:    '+',
               re.states.SCHEDULING: '|',
               re.states.SUSPENDED:  '-',
               re.states.DONE:       ' ',
               re.states.FAILED:     '!',
               re.states.CANCELED:   'X'}


    # --------------------------------------------------------------------------
    #
    def __init__(self, replicas, replica_cycles, selection_criteria,
                       inputs, outputs, resource):

        self._replicas  = replicas
        self._cycles    = replica_cycles
        self._en_size   = len(replicas)
        self._sel_crit  = selection_criteria
        self._waitlist  = list()

        self._sel_alg   = _sel_algs.get(self._sel_crit['select_alg'])
        self._ex_alg    = _exc_algs.get(self._sel_crit['exchange_alg'])

        # if the configured algorithms are not known (not hard-coded in RX),
        # then assume they point to user specified files and load them
        if not self._sel_alg:
            filename, funcname = self._sel_crit['select_alg'].split(':')
            syms = ru.import_file(filename)
            self._sel_alg = syms['functions'][funcname]

        if not self._ex_alg:
            filename, funcname = self._sel_crit['exchange_alg'].split(':')
            syms = ru.import_file(filename)
            self._ex_alg = syms['functions'][funcname]

        for r in replicas:
            r._initialize(check_ex=self._check_exchange,
                          check_res=self._check_resume)

        self._lock = mt.Lock()

        rmq_host = str(resource.get('rmq_host', 'localhost'))
        rmq_port = int(resource.get('rmq_port', '5672'))

        re.AppManager.__init__(self, autoterminate=True,
                                     hostname=rmq_host, port=rmq_port)

        rd = copy.deepcopy(resource)
        if 'rmq_host' in rd: del(rd['rmq_host'])
        if 'rmq_port' in rd: del(rd['rmq_port'])

        self.resource_desc = rd
        self.shared_data   = inputs
        self.outputs       = outputs

        self._log  = ru.Logger('radical.repex')
        self._dout = open('dump.log', 'a')
        self._dump(msg='startup')

        # run the replica pipelines
        self.workflow = set(self._replicas)

        # write exchange algorithm to disk (once)
        self._ex_alg_file = './exchange_algorithm.py'
        with open(self._ex_alg_file, 'w') as fout:
            fout.write('#!/usr/bin/env python\n\n%s\n\n%s()\n\n' %
                       (inspect.getsource(self._ex_alg),
                        self._ex_alg.__name__))


    # --------------------------------------------------------------------------
    #
    def run(self):
        '''
        run the replica exchange pipelines, and after all is done, fetch the
        requested output data
        '''

        re.AppManager.run(self)


    # --------------------------------------------------------------------------
    #
    def _dump(self, msg=None, special=None, glyph=None ):

        if not self._dout:
            return

        if not msg:
            msg = ''

        if not self._dout:
            return

        self._dout.write(' | %7.2f |' % (time.time() - self._t_0))
        for r in self._replicas:
            if special and r in special:
                self._dout.write('%s' % glyph)
            else:
                self._dout.write('%s' % self._glyphs[r.state])
        self._dout.write('| %s\n' % msg)
        self._dout.flush()


    # --------------------------------------------------------------------------
    #
    def terminate(self):

        self._log.debug('exc term')
        self._dump(msg='terminate', special=self._replicas, glyph='=')
        if self._dout:
            self._dout.close()
            self._dout = None

        # we are done!
        re.AppManager.terminate(self)


    # --------------------------------------------------------------------------
    #
    def _check_exchange(self, replica):

        # method races when concurrently triggered by multpiple replicas
        with self._lock:

            self._waitlist.append(replica)

            ex_list   = None
            new_wlist = None

            # invoke the user defined selection algorithm
            try:
                ex_list, new_wlist = self._sel_alg(waitlist=self._waitlist,
                                                   criteria=self._sel_crit,
                                                   replica=replica)
            except Exception as e:
                self._log.exception('selection algorithm failed: %s' % e)

            # check if the user found something to exchange
            if not ex_list:
                # nothing to do, suspend this replica and wait until we get more
                # candidates and can try again
                self._log.debug('%s %s no  - suspend', replica.rid, replica._uid)
                replica.suspend()
                self._dump()
                return

            # Seems we got something - make sure its valid:  exchange list and
            # new wait list must be proper partitions of the original waitlist:
            #   - make sure no replica is lost
            #   - make sure that replicas are not in both lists
            missing = len(self._waitlist) - len(ex_list) - len(new_wlist)
            if missing:
                raise ValueError('%d replicas went missing' % missing)

            for r in self._waitlist:
                if r not in ex_list and r not in new_wlist:
                    raise ValueError('replica %s (%s) missing'
                                    % r, r.properties)

            if replica not in ex_list:
                raise ValueError('active replica (%s) not in exchange list %s)'
                                % (replica.rid, [r.rid for r in ex_list]))

            # lists are valid - use them
            self._waitlist = new_wlist

            self._log.debug('%s %s yes - exchange', replica.rid, replica._uid)
            msg = " > %s: %s" % (replica.rid, [r.rid for r in ex_list])
            self._dump(msg=msg, special=ex_list, glyph='v')

            # we have a set of exchange candidates.  The current replica is
            # tasked to host the exchange task.
            replica.add_ex_stage(ex_list, self._ex_alg_file)


    # --------------------------------------------------------------------------
    #
    def _check_resume(self, replica):

        self._dump()
        self._log.debug('%s %s check resume', replica.rid, replica._uid)

        resumed = list()  # list of resumed replica IDs

        msg = " < %s: %s" % (replica.rid, [r.rid for r in replica.exchange_list])
        self._dump(msg=msg, special=replica.exchange_list, glyph='^')

        # after a successfull exchange we revive all participating replicas.
        # For those replicas which did not yet reach min cycles, add an md
        # stage, all others we let die and add a new md stage for them.
        for _replica in replica.exchange_list:

            if _replica.cycle <= self._cycles:
                _replica.add_md_stage()

            # Make sure we don't resume the current replica
            if replica.rid != _replica.rid:

                self._log.debug('%s %s resume', _replica.rid, replica._uid)
                _replica.resume()
                resumed.append(_replica.uid)

        return resumed


# ------------------------------------------------------------------------------

