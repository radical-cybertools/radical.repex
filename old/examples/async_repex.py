#!/usr/bin/env python

import time, os
import random
import writeInputs
import threading as mt
import tarfile
import radical.entk  as re
import radical.utils as ru
import radical.analytics as ra

#os.environ['RADICAL_VERBOSE'] = 'INFO'
os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'

os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://smush:key1209@ds111336.mlab.com:11336/repex_2'
           


RMQ_PORT = int(os.environ.get('RMQ_PORT', 32769))
#SANDER   = ['/home/scm177/mantel/AMBER/amber14/bin/sander']
SANDER = ['/pylon5/mr560ip/mushnoor/AMBER/amber14/AmberTools/bin/sander']

t_0 = time.time()

# ------------------------------------------------------------------------------
#
def void():

    pass


# ------------------------------------------------------------------------------
#
class ReplicaExchange(re.AppManager):

    _glyphs = {re.states.INITIAL:    '+',
               re.states.SCHEDULING: '|',
               re.states.SUSPENDED:  '-',
               re.states.DONE:       ' ',
               re.states.FAILED:     '!',
               re.states.CANCELED:   'X'}


    # --------------------------------------------------------------------------
    #
    def __init__(self, ensemble_size, exchange_size, window_size, md_cycles, min_temp, max_temp, timesteps, basename, executable, cores):

        self._en_size = ensemble_size
        self._ex_size = exchange_size
        self._window_size = window_size
        self._cycles  = md_cycles
        self._min_temp      = min_temp
        self._max_temp      = max_temp
        self._timesteps     = timesteps
        self._basename      = basename
        self._executable    = executable
        self._cores         = cores
        self._lock = mt.Lock()
        self._log  = ru.Logger('radical.repex.exc')
        self._dout = open('dump.log', 'a')

        re.AppManager.__init__(self, autoterminate=False, port=32769) 
        # self.resource_desc = {"resource" : 'local.localhost',
        #                       "walltime" : 30,
        #                       "cpus"     : 8}               
        self.resource_desc = {"resource"      : "xsede.bridges",
 
                              "walltime"      : 60,
                              "cpus"          : 24,
                              "gpus_per_node" : 0,
                              "access_schema" : "gsissh",
                              "queue"         : "RM",
                              "project"       : "mr560ip"
             
                              }



        
        self._sbox          = '$Pipeline_untarPipe_Stage_untarStg_Task_untarTsk'
        self._cnt           = 0  # count exchanges
        self._replicas = list()
        self._waitlist = list()

        # create the required number of replicas
        for i in range(self._en_size):

            replica = Replica(check_ex  = self._check_exchange,
                              check_res = self._check_resume,
                              rid       = i,
                              sbox      = self._sbox,
                              cores     = self._cores, 
                              exe       = self._executable)

            self._replicas.append(replica)

        self._dump(msg='startup')

        # run the replica pipelines
        #self.setup()
        #self.workflow = set(self._replicas)
        #self.run() 

    def setup(self):



        # prepare input for all replicas
        writeInputs.writeInputs(max_temp=self._max_temp,
                                min_temp=self._min_temp,
                                replicas=self._en_size,
                                timesteps=self._timesteps,
                                basename=self._basename)

        # and tar it up
        tar = tarfile.open("input_files.tar", "w")
        for name in [self._basename + ".prmtop",
                     self._basename + ".inpcrd",
                     self._basename + ".mdin"]:
            tar.add(name)

        for replica in self._replicas:
            tar.add  ('mdin-%s-0' % replica.rid) #how does this work
            os.remove('mdin-%s-0' % replica.rid)
            
        tar.close()

        # create a single pipeline with one stage to transfer the tarball
        task = re.Task()
        task.name              = 'untarTsk'
        task.executable        = ['python']
        task.upload_input_data = ['untar_input_files.py', 'input_files.tar']
        task.arguments         = ['untar_input_files.py', 'input_files.tar']
        task.cpu_reqs          = {'processes' : 1,
                                'thread_type' : None, 
                                'threads_per_process': 1, 
                                'process_type': None}
        task.post_exec         = []

        stage = re.Stage()
        stage.name = 'untarStg'
        stage.add_tasks(task)

        #setup = re.Pipeline()
        #setup.name = 'untarPipe'
        #setup.add_stages(stage)

        setup_pipeline = re.Pipeline()
        setup_pipeline.name = 'untarPipe'
        setup_pipeline.add_stages(stage)
        return [setup_pipeline]

        # run the setup pipeline   #uncomment these if you can reproduce the problem
        #self.workflow = set([setup]) 
        #self.run() 

    # --------------------------------------------------------------------------
    #
    def _dump(self, msg=None, special=None, glyph=None ):

        if not msg:
            msg = ''

        self._dout.write(' | %7.2f |' % (time.time() - t_0))
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
        self._dout.close()

        # we are done!
        self.resource_terminate()

    # --------------------------------------------------------------------------
    #
    def execute(self):

        self.workflow = set(self.setup()) 
        self.run()
        self.workflow = set(self._replicas)
        self.run() 


    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    #
    def _check_exchange(self, replica):

        # This method races when concurrently triggered by multpiple replicas,
        # and it should be guarded by a lock.
        with self._lock:

            self._log.debug('=== %s check exchange : %d >= %d?',
                      replica.rid, len(self._waitlist), self._ex_size)

            self._waitlist.append(replica)
            msg = " > %s: %s" % (replica.rid, [r.rid for r in self._waitlist])
            self._dump(msg=msg, special=self._waitlist, glyph='v')

            exchange_list = self._find_exchange_list(self._ex_size, self._window_size , current_replica=replica)

            if not exchange_list:
                # nothing to do, Suspend this replica and wait until we get more
                # candidates and can try again
                self._log.debug('=== %s no  - suspend', replica.rid)
                replica.suspend()
                self._dump()
                return

            self._log.debug('=== %s yes - exchange', replica.rid)
            msg = " > %s: %s" % (replica.rid, [r.rid for r in exchange_list])
            self._dump(msg=msg, special=exchange_list, glyph='v')

            # we have a set of exchange candidates.  The current replica is

            # tasked to host the exchange task.
            replica.add_ex_stage(exchange_list)


    # --------------------------------------------------------------------------
    #
    def _find_exchange_list(self, exchange_size, window_size, current_replica):
        '''
        This is a function that accepts as input the sorted waitlist and 
        the number of replicas needed for an exchange. It then generates sublists from 
        the sorted waitlist. These sublists contain "compatible" replicas 
        that can proceed to perform exchanges amongst themselves.
        '''
        waitlist = self._waitlist
        if len(waitlist) < exchange_size:
            return

        exchange_list = list()
        sorted_waitlist = sorted(waitlist, key = lambda x: x.rid)

        for rep in sorted_waitlist:  

            start_index=sorted_waitlist.index(rep)
            end_index = start_index + exchange_size -1
            try:
                delta = sorted_waitlist[end_index].rid - sorted_waitlist[start_index].rid
                exchange_list = sorted_waitlist[start_index:end_index+1]

                if len(exchange_list) == exchange_size and current_replica in exchange_list and delta < window_size:

            
                    for rep in exchange_list:
                        waitlist.remove(rep)
                    return exchange_list

                else:
                    continue

            except:

                return


    # --------------------------------------------------------------------------
    #
    def _check_resume(self, replica):

        self._dump()
        self._log.debug('=== %s check resume', replica.rid)

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

                try:
                    self._log.debug('=== %s resume', _replica.rid)
                    _replica.resume()
                    resumed.append(_replica.uid)
                except:
                    print "This replica is already resumed"

        return resumed


# ------------------------------------------------------------------------------
#
class Replica(re.Pipeline):
    '''
    A `Replica` is an EnTK pipeline which consists of alternating md and
    exchange stages.  The initial setup is for one MD stage - Exchange and more
    MD stages get added depending on runtime conditions.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, check_ex, check_res, rid, sbox, cores, exe):

        self._check_ex  = check_ex
        self._check_res = check_res
        self._rid       = rid
        self._sbox      = sbox
        self._cores     = cores
        self._exe       = exe

        self._cycle     = 0     # initial cycle
        self._ex_list   = None  # list of replicas used in exchange step

        re.Pipeline.__init__(self)
        self.name = 'p_%s' % self.rid
        self._log = ru.Logger('radical.repex.rep')

        # add an initial md stage
        self.add_md_stage()


    @property
    def rid(self):      return self._rid

    @property
    def cycle(self):    return self._cycle


    # --------------------------------------------------------------------------
    #
    @property
    def exchange_list(self):

        return self._ex_list


    # --------------------------------------------------------------------------
    #
    def add_md_stage(self):

        self._log.debug('=== %s add md', self.rid)

        rid   = self._rid
        cycle = self._cycle
        sbox  = self._sbox
        cores = self._cores
        exe   = self._exe



        task = re.Task()
        task.name            = 'mdtsk-%s-%s'               % (      rid, cycle)
        if cycle == 0:
            task.link_input_data = ['%s/inpcrd > inpcrd-%s-%s' % (sbox, rid, cycle),
                                    '%s/prmtop'                % (sbox),
                                    '%s/mdin-%s-%s > mdin'     % (sbox, rid, cycle)]
        else:
            cycle_0 = '0'            
            task.link_input_data =  ['%s/inpcrd-%s-%s'         % (sbox, rid, cycle),
                                     '%s/prmtop'               % (sbox),
                                     '%s/mdin-%s-%s > mdin'    % (sbox, rid, cycle_0)]
                                      #['%s/mdcrd-out-%s-%s > inpcrd-%s-%s' % (sbox, rid, cycle, rid, cycle),
                                    

        task.arguments       = ['-O', 
                                '-i',   'mdin', 
                                '-p',   'prmtop', 
                                '-c',   'inpcrd-%s-%s'     % (      rid, cycle), 
                                '-o',   'out',
                                '-x',   '%s/mdcrd-%s-%s'   % (sbox, rid, cycle+1),
                                '-r',   '%s/inpcrd-%s-%s'  % (sbox, rid, cycle+1),
                                '-inf', '%s/mdinfo-%s-%s'  % (sbox, rid, cycle)]
        task.executable      = SANDER #[exe]
        task.cpu_reqs        = {'processes' : cores,
                                'thread_type' : None, 
                                'threads_per_process': 1, 
                                'process_type': None}
        task.pre_exec        = ['module load intel/19.3', 'module load python3/intel_3.6.3'] #This will be different for different MD engines.

        stage = re.Stage()
        stage.add_tasks(task)
        stage.post_exec = self.check_exchange   #_after_md
        self.add_stages(stage)


    # --------------------------------------------------------------------------
    #
    def check_exchange(self):
        '''
        after an md cycle, record its completion and check for exchange
        '''

        self._cycle += 1
        self._check_ex(self)


    # --------------------------------------------------------------------------
    #
    def add_ex_stage(self, exchange_list):

        self._log.debug('=== %s add ex: %s', self.rid,
                                             [r.rid for r in exchange_list])

        self._ex_list = exchange_list  
        self._res_list = exchange_list
        

        task = re.Task()
        task.name       = 'extsk'
        task.executable = ['/opt/packages/python/2_7_11_gcc/bin/python2.7']#['/home/scm177/VirtualEnvs/Env_RepEx/bin/python']
        task.pre_exec   = ['module unload python3/intel_3.6.3','module load python/2.7.11_gcc', 'module load intel/19.3']
        task.upload_input_data = ['t_ex_gibbs.py']
        task.arguments  = ['t_ex_gibbs.py', self._sbox]

        for replica in exchange_list:  
            rid   = replica.rid 
            cycle = replica.cycle 
            task.link_input_data.append('%s/mdinfo-%s-%s' % (self._sbox, rid, cycle-1))  # % (self._sbox, rid, cycle))
        stage = re.Stage()
        stage.add_tasks(task)
            
        stage.post_exec = self.check_resume  #_after_ex

        self.add_stages(stage)


    # --------------------------------------------------------------------------
    #
    def check_resume(self):
        '''
        after an ex cycle, trigger replica resumption
        '''
        self._log.debug('=== check resume %s', self.rid)
        return self._check_res(self)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    exchange = ReplicaExchange(ensemble_size = 64, 
                               exchange_size = 64, 
                               window_size   = 64,
                               md_cycles     = 10, 
                               min_temp      = 300,
                               max_temp      = 400,
                               timesteps     = 1000,  # Timestep is 2fs. If a cycle is 2500 steps, EAF is 1/5 ps^-1  
                               basename      = 'ace-ala', 
                               executable    = SANDER, 
                               cores         = 1)
    exchange.execute()
    exchange.terminate()

    #pwd = os.getcwd()
    #sessionname = ReplicaExchange.sid
    #print sessionname
    #session = ra.Session(sid   = sessionname,
                         #stype = 'radical.entk',
                         #src = pwd)
    #total                   = session.filter(etype='task', inplace=False)
    #total_durations = total.duration([re.states.SCHEDULED, re.states.DONE])
    #print "total duration is " , total_durations