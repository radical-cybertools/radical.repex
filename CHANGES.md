
  - For a list of bug fixes, see
    https://github.com/radical-cybertools/radical.repex/ \
            issues?q=is%3Aissue+is%3Aclosed+sort%3Aupdated-desc
  - For a list of open issues and known problems, see
    https://github.com/radical-cybertools/radical.repex/ \
            issues?q=is%3Aissue+is%3Aopen+


1.61.0 Release                                                        2024-07-25
--------------------------------------------------------------------------------

  - sync with RCT stack


1.60.0 Release                                                        2024-05-10
--------------------------------------------------------------------------------

  - sync with RU


1.52.0 Release                                                        2024-04-15
--------------------------------------------------------------------------------

  - fix for setuptools upgrade


1.47.0 Release                                                        2024-02-08
--------------------------------------------------------------------------------

  - maintenance


1.46.0 Release                                                        2024-01-11
--------------------------------------------------------------------------------

  - pypi fix


1.44.0 Release                                                        2024-01-10
--------------------------------------------------------------------------------

  - maintenance


1.16.0 Release                                                        2022-08-15
--------------------------------------------------------------------------------

  - clean old files


v0.74.0 Release                                                       2022-03-21
--------------------------------------------------------------------------------

  - remove temporary setup files


v0.73.0 Release                                                       2019-11-22
--------------------------------------------------------------------------------

  - add example for external exchange alg select_by_random()
  - add rx profile events
  - fix data staging
  - expose RMQ_HOST/RMQ_PORT
  - extract write_inputs script
  - fix alg return type
  - fix data staging logic, termination logic (allow empty waitlists)
  - Getting ready for full testing
  - linting
  - modify test for wl_size>ex_size
  - support pre_exec
  - Syncing repex with latest RCT changes.
  - terminate when running out of replicas


v0.72.0 Release                                                       2019-09-22
--------------------------------------------------------------------------------

  - recover original history from SM
  - clean out large files
  - repo restrucuting

      
v0.70.0 Release                                                       2019-07-07
--------------------------------------------------------------------------------

  -  move sliding windo alg here
  -  add workload description in json
  -  fix exchange list verification


Version 0.0.1 release                                                 2014-10-31
--------------------------------------------------------------------------------

  -  initial commit for radical project 'repex'


--------------------------------------------------------------------------------

  - (tag: archive/feature/lfs) Sync updated
  - 1D Synchronous Exchange Test
  - AMBER class added
  - AMBER class finalized
  - AMBER kernel+BlueWaters scripts
  - Added documentation for DA scheduler algorithm use case
  - Bag of Tasks with EnTK 0.6.2
  - Calculate exchange matrix
  - Correctly parse local.localhost resconfig
  - Create Temperature Exchange Method
  - DA Scheduler test case
  - Delete EnTK_Profiles.ipynb
  - Delete Exch_Rand.py
  - Delete Exchange_Calculator.py
  - Delete Exchange_Method.py
  - Delete FNF.itp
  - Delete Input_Files.tar
  - Delete SyncEx.py
  - Delete SyncEx.py~
  - Delete driver.py
  - Delete driverMultipleAppmanager.py
  - Delete driver_main.py
  - Delete exchangePairs.dat
  - Delete in.gro
  - Delete in.mdp
  - Delete in.top
  - Delete inpcrd
  - Delete martini_v2.2.itp
  - Delete mdin
  - Delete multiple_exchanges.py
  - Delete old_driver.py
  - Delete prmtop
  - Delete radical.entk.appmanager.0000.prof
  - Delete radical.entk.resource_manager.0000.prof
  - Delete radical.entk.task_manager.0000-obj.prof
  - Delete radical.entk.task_manager.0000-proc.prof
  - Delete radical.entk.wfprocessor.0000-obj.prof
  - Delete radical.entk.wfprocessor.0000-proc.prof
  - Delete resconfig_comet.json
  - Delete resconfig_supermic.json
  - Delete run.py~
  - Delete session_duration.py
  - EnTK0.7 API change
  - Ex Method hardcoding removed+fixes towards issue #18
  - Exchange Frequency Plots
  - Issue #13 fixed
  - Issue 18 addressed
  - LFS prelim data
  - MD Executable Path-semi fixed
  - PEP8 compliance using yapf
  - Session added for Profiling session
  - Stable AMBER workload
  - Stage 1 choked, investigating fix
  - Sync workflow remove conflict
  - TTX vs Exchange Frequency Scaling Data
  - TX vs ExFreq
  - Update .gitignore
  - Update README.md
  - Update Sync.py
  - Update _version.py
  - Update driver.py
  - Update driver_bw.py
  - Update driver_comet.py
  - Update driver_supermic.py
  - Update readme for how to run instructions.
  - Update repex
  - Update resconfig_local.json
  - Update simconfig.json
  - Update simconfig_local.json
  - Update test_pipeline.py
  - Update untar_input_files.py
  - Update writeInputs.py
  - Updates to Async implementation
  - WIP
  - adaptivity scheme changed
  - add GROMACS task class
  - add mdinfo file reader to exchange calculator
  - adding repex to bin
  - address issue 19
  - agentside profiles added
  - api
  - async implementation w/ partial adaptivity
  - automated input file building
  - bugfix towards incorrect energy file reading
  - cleaning up accidental commit of pilot files
  - cleanup
  - cleanup exchange methods dir
  - comments for easier readability
  - correct Metropolis criterion
  - correct referencing of replicas before data movement
  - documentation
  - documentation WIP
  - documentation update
  - examples added
  - examples added to the documentation
  - examples for BW
  - examples readme
  - exchange task fails to copy energy files
  - experimental async
  - fix_issue17
  - fixed GROMACS class with correct post exec to extract energies from .edr files
  - fixed energy files copy issue
  - fixing test
  - fixing the MPI problem
  - folder structure fixed
  - frequency distributions
  - independence sampling scheme implemented for T-exchange to address #18
  - init pipeline now tars and untars
  - latest commit, infinite loop resolved, but all pipelines attempting to resume
  - legend added
  - localhost execution fixed
  - logfiles for failing units
  - longer runtimes
  - longer walltime
  - md scheduling addressed
  - minor edit to SyncEx.py
  - minor edits
  - minor fix
  - minorly restructured code
  - more fixes towards correctly parsing localhost resconfig
  - more plots
  - more scaling data
  - new FD's
  - new data with profiles
  - new profiles
  - partial async implementation
  - performance
  - potential Sync RE workflow
  - potentially fixed weak scaling
  - profiler works now
  - profiles are there now
  - py files temporarily added
  - randex module
  - readme updated
  - readme updated to reflect documentation
  - remove unnecessary lines
  - remove unnecessary variables from TempEx.py
  - rename main script
  - reorg
  - reorganize repo
  - run_fixed
  - saving some files before cleanup
  - scaling data
  - scaling data for ttx vs ex freq
  - scaling decomposition data
  - scaling plot
  - scaling plots
  - setup.py update
  - sliding window commit to devel
  - src folder removed
  - stages decomposed
  - stagewise decomposition
  - starting to add a profiler
  - tarballs for BoT mode execution
  - temporary, hackish fix for no untar script
  - test
  - test script for async
  - testing uids
  - travis update
  - update devel
  - update documentation
  - update driver
  - update installation instructions
  - update main script
  - update readme
  - update test
  - update test suite
  - update test to reflect latest build
  - update to new workflow
  - update user guide with resconfig
  - updated async + EnTK examples for reference
  - updates
  - updates to devel
  - updates to driverMultipleAppmanager and driverMain
  - version bump
  - version bump for real
  - weak scaling tweak
