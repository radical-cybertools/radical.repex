
<img src="https://travis-ci.org/radical-cybertools/radical.repex.svg?branch=master" alt="Travis CI"/>

# ReplicaExchange

Replica-Exchange (RE) is a family of simulation techniques used to enhance
sampling and more thoroughly explore phase space of simulations. RE simulations
involve the concurrent execution of independent simulations which interact and
exchange information. Replica Exchange (RE), a method devised as early as 1986
by Swendsen et. al., is a popular technique to enhance sampling in molecular
simulations. Replica Exchange Molecular Dynamics (REMD) was first formulated in
1999 by Sugita and Okamoto. Initially REMD was used to perform exchanges of
temperatures, but was later extended to perform other exchange types. Over the
years, REMD has been adopted by many scientific disciplines including chemistry,
physics, biology and materials science.

Most RE implementations however are confined within their parent molecular
dynamics (MD) packages. This is limiting because it becomes difficult to
implement new RE methods, or apply exchange methods across MD packages.

RepEx is designed to be scalable, flexible, and above all, extensible. New
developments in replica exchange (RE) should not only be limited to specific MD
packages in which they were developed. RepEx aims to decouple the development of
new advanced sampling algorithms from specific MD engines, and allows users to
easily implement their cumstom RE algorithms and plug them into RepEx. RepEx
also supports multiple MD engines including AMBER and GROMACS.

RepEx is available under the MIT License.


# Documentation

RepEx replica exchange package implemented via the Ensemble Toolkit 0.7 API.
Documentation can be found at: https://repex-30.readthedocs.io/en/latest/



Run the base example as follows:

```
bin/radical-repex examples/workload_test.json examples/resource_local.json
```

While that example is running, a number of state update messages will be printed
on screen.  One can also follow the overall progress of the run by watching the
created `dump.log` file:

```
$ tail -F dump.log
 |    1.30 |++++++++++++++++++++++++++++++++| startup
 |   78.45 |||||||||||||||||||||||||||||-||||
 |   78.49 ||||||||||||-||||||||||||||||-||||
 |   78.51 ||||||||||||-||||-|||||||||||-||||
 |   78.55 ||||||||||||-||||-|||||||||||-|-||
 |   78.59 ||||||||||||-||||-||||||||-||-|-||
 |   78.62 ||||||-|||||-||||-||||||||-||-|-||
 |   78.64 ||||||-||||--||||-||||||||-||-|-||
 |   78.67 ||||||v||||vv|||vv||||||||v||v|v||  > rep.0015: ['rep.0005', 'rep.0011', 'rep.0016', 'rep.0025', 'rep.0028', 'rep.0010', 'rep.0015', 'rep.0030']
 |   78.71 ||||||-||||--||||-|||-||||-||-|-||
 |   78.76 |-||||-||||--||||-|||-||||-||-|-||
 |   78.77 |-||||-||||--||||-|||-||||-||---||
 |   78.80 |-|||--||||--||||-|||-||||-||---||
 |   78.83 |-|||--||||--||||-|||-|||--||---||
 |   78.86 |-|||--|||---||||-|||-|||--||---||
 |   78.88 |-|||--|||---||-|-|||-|||--||---||
 |   78.90 |v|||v-|||v--||v|-||vv|||v-||-v-||  > rep.0019: ['rep.0020', 'rep.0014', 'rep.0019', 'rep.0029', 'rep.0024', 'rep.0000', 'rep.0009', 'rep.0004']
 |   79.03 |-||---|||---||-|-|||-|||--||---||
 |   79.07 |-||---|||---||-|-|||-||---||---||
 |   79.13 |-||---|||---|--|-|||-||---||---||
 |   79.15 |-||---||----|--|-|||-||---||---||
 |   79.17 |-|----||----|--|-|||-||---||---||
 |   79.20 |-|----||----|--|-|-|-||---||---||
 |   79.23 |-|----||----|--|-|-|-||---|----||
 |   79.26 |-|vv--||v---|v-|-|v|-|vv--|v---||  > rep.0022: ['rep.0003', 'rep.0018', 'rep.0023', 'rep.0022', 'rep.0008', 'rep.0002', 'rep.0027', 'rep.0013']
 |   79.30 |-|----||----|--|-|-|-||---|----||
 |   79.30 |-|---^||--^^|--^^|-|-||--^|-^-^||  < rep.0015: ['rep.0005', 'rep.0011', 'rep.0016', 'rep.0025', 'rep.0028', 'rep.0010', 'rep.0015', 'rep.0030']
 |   79.34 |-|---||---|||--|||-|-||--||-|-|||
 |   79.37 |-|---||---||---|||-|-||--||-|-|||
 |   79.39 |-|---||---||---|||-|-||--||-|-|||
 |   79.39 |^|--^||--^||--^|||-^^||-^||-|^|||  < rep.0019: ['rep.0020', 'rep.0014', 'rep.0019', 'rep.0029', 'rep.0024', 'rep.0000', 'rep.0009', 'rep.0004']
 |   79.56 |||--|||--|||--|||--||||-|||-|||||
 |   79.72 |||--|||--|||--|||--||||-|||-|||-|
 |   79.76 ||---|||--|||--|||--||||-|||-|||-|
 |   79.81 ||---|||--|||--|||--||||-|||-|||-|
 |   79.81 ||-^^|||-^|||-^|||-^|||^^|||^|||-|  < rep.0022: ['rep.0003', 'rep.0018', 'rep.0023', 'rep.0022', 'rep.0008', 'rep.0002', 'rep.0027', 'rep.0013']
 |   79.96 ||-|||||-||||-||||-|||-|||||||||-|
 |   80.04 ||-|||||-||||-||||-|||-||||-||||-|
 |   80.12 ||v||||vv||||v||||v|||v||||v||||v|  > rep.0006: ['rep.0012', 'rep.0001', 'rep.0006', 'rep.0017', 'rep.0007', 'rep.0026', 'rep.0021', 'rep.0031']
 |   80.66 ||-|||||-||||-||||-|||-||||-||||-|
 |   80.66 ||^||||^^||||^||||^|||^||||^||||^|  < rep.0006: ['rep.0012', 'rep.0001', 'rep.0006', 'rep.0017', 'rep.0007', 'rep.0026', 'rep.0021', 'rep.0031']
 |  126.39 |-||||||||||||||||||||||||||||||||
 |  126.45 |-|||||||||||||||||||-||||||||||||
 ```

 More detailed log traces can be found in `radical.repex.log`.
