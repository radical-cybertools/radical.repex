
import copy

import time
import inspect

import radical.entk  as re
import radical.utils as ru

from   .algorithms import exchange_alg_prefix
from   .replica    import Replica
from   .utils      import last_task


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
    def __init__(self, workload, resource, replicas=None):

        # initialize EnTK
        super().__init__(autoterminate=True)

        self._uid  = ru.generate_id('rx')
        self._prof = ru.Profiler('radical.repex')
        self._prof.prof('create', uid=self._uid)

        self._workload = ru.Config(cfg=workload)
        self._resource = ru.Config(cfg=resource)
        self._replicas = replicas

        # replicas may need resource specific pre_exec directives
        self._workload.pre_exec = self._resource.pre_exec

        assert(self._workload.config.replicas or self._replicas)
        assert(self._workload.config.cycles)

        self._cycles   = self._workload.config.cycles
        self._waitlist = list()

        # load prepare, selection and exchange algorithms
        self._pre_alg = self._load_algorithm(self._workload.prepare.algorithm)
        self._sel_alg = self._load_algorithm(self._workload.selection.algorithm)
        self._exc_alg = self._load_algorithm(self._workload.exchange.algorithm)

        assert(self._pre_alg),  'preparation algorithm missing'
        assert(self._sel_alg),  'selection algorithm missing'
        assert(self._exc_alg),  'exchange algorithm missing'

        if self._replicas:
            # replicas are passed down - no need to create them
            self._workload.config.replicas = len(self._replicas)
        else:
            # create replicas as specified in the workload config
            self._replicas = [Replica(workload=self._workload)
                                for _ in range(self._workload.config.replicas)]

        # initialize all replica pipelines, i.e, create the initial MD stages
        for r in self._replicas:
            r._initialize(check_ex=self._check_exchange,
                          check_res=self._check_resume,
                          sid=self.sid, prof=self._prof)

        self._lock = ru.Lock(name='rx')

        rd = copy.deepcopy(self._resource)
        if 'pre_exec' in rd: del(rd['pre_exec'])

        self.resource_desc = rd

        self._log  = ru.Logger('radical.repex')
        self._dout = open('dump.log', 'a')
        self._dump(msg='startup')

        # run the replica pipelines
        self.workflow = set(self._replicas)


    # --------------------------------------------------------------------------
    #
    def run(self):
        '''
        run the replica exchange pipelines, and after all is done, fetch the
        requested output data
        '''

        # run the preparator, the returned file names are to be staged
        fnames = ru.as_list(self._pre_alg(self._workload))

        # stage additional data if so configured
        if self._workload.data.inputs not in fnames:
            fnames.append(self._workload.data.inputs)

        # write exchange algorithm to disk (once), and then stage with every
        # exchange task
        self._ex_alg_file = 'exchange_algorithm.py'
        with open('%s/%s' % (self._workload.data.inputs, self._ex_alg_file),
                  'w') as fout:
            fout.write(exchange_alg_prefix % (inspect.getsource(self._exc_alg),
                                              self._exc_alg.__name__))

        # stage the input data
        self.shared_data = fnames

        # run will submit all pipelines to EnTK
        super().run()


    # --------------------------------------------------------------------------
    #
    def _load_algorithm(self, alg_spec):

        filename, funcname = alg_spec.split(':')
        symbols = ru.import_file(filename)

        return symbols['functions'][funcname]


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
        super().terminate()


    # --------------------------------------------------------------------------
    #
    def _check_exchange(self, replica):

        # for this replica, run the selection algorithm and check if this
        # replica is eligible for an exchange.

        # method races when concurrently triggered by multiple replicas
        with self._lock:

            # this replica is also eligible for exchange, add it to the waitlist
            self._waitlist.append(replica)

            ex_list   = None
            new_wlist = None

            # invoke the user defined selection algorithm
            try:
                ex_list, new_wlist = self._sel_alg(
                        waitlist=self._waitlist,
                        selection=self._workload.selection,
                        replica=replica)

                self._log.debug('sel: %4d -> %4d + %4d = %4d',
                        len(self._waitlist), len(ex_list), len(new_wlist),
                        len(ex_list) + len(new_wlist))

            except Exception as e:
                self._log.exception('selection algorithm failed: %s' % e)

            # check if the user found something to exchange
            if not ex_list:

                # nothing to do, suspend this replica and wait until we get more
                # candidates and can try again
                self._log.debug('%5s %s no  - suspend',
                                replica.rid, replica._uid)
                replica.suspend()
                self._dump()

                # waiting for more replicas only makes sense if any others are
                # still in `SCHEDULING` state
                states = dict()
                for r in self._replicas:
                    if r.state not in states: states[r.state] = 1
                    else                    : states[r.state] += 1
                self._log.debug('=== %s', ['%s=%s' % (k, v) for k, v in states.items()])

                if states.get(re.states.SCHEDULING):
                    # some more replicas are active - wait for those to complete
                    # the exchange list
                    return

                # did not find any active replics, thus the exchange list will
                # never grow and a new exchange will never happen - terminate
                self._log.warn('=== terminating due to lack of active replicas')
                raise RuntimeError('terminating due to lack of active replicas')


            # Seems we got an exchange list - check it: exchange list and
            # new wait list must be proper partitions of the original waitlist:
            #   - make sure no replica is lost
            #   - make sure that replicas are not in both lists
            assert(new_wlist is not None)
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

            self._log.debug('%5s %s yes - exchange', replica.rid, replica._uid)
            msg = " > %s: %s" % (replica.rid, [r.rid for r in ex_list])
            self._dump(msg=msg, special=ex_list, glyph='v')

            # we have a set of exchange candidates.  The current replica is
            # tasked to host the exchange task.
            replica.add_ex_stage(ex_list, self._ex_alg_file, self.sid)


    # --------------------------------------------------------------------------
    #
    def _check_resume(self, replica):

        # this method is called after an exchange cycle has completed for the
        # given replica.
        #
        # For all replicas which participated in the exchange,
        # add a new MD stage for them and resume them (do not resume *this*
        # replica, as it is obviously running).

        self._dump()
        self._log.debug('%5s %s check resume', replica.rid, replica._uid)

        resumed = list()  # list of resumed replica IDs

        msg = " < %s: %s" % (replica.rid,
                             [r.rid for r in replica.exchange_list])
        self._dump(msg=msg, special=replica.exchange_list, glyph='^')

        exchange = last_task(replica)

        # after a successful exchange we revive all participating replicas.
        # For those replicas which did not yet reach min cycles, add an MD
        # stage, all others we let die and add a new MD stage for them.
        for _replica in replica.exchange_list:

            # add a new MD stage for all replicas which did not yet reach the
            # required number of cycles
            if _replica.cycle <= self._cycles:
                last = bool(_replica.cycle == self._cycles)
                _replica.add_md_stage(exchanged_from=exchange,
                                      sid=self.sid, last=last)

            # Make sure we don't resume the current replica
            if replica.rid != _replica.rid:

                self._log.debug('%5s %s resume', _replica.rid, replica._uid)
                if _replica.state == re.states.SUSPENDED:
                    _replica.resume()
                resumed.append(_replica.uid)

        # return the list of resumed replica IDs
        return resumed


# ------------------------------------------------------------------------------

