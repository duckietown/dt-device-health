"""
Tegrastats example output:
RAM 1766/3964MB (lfb 197x4MB) SWAP 0/2048MB (cached 0MB) CPU [24%@1224,15%@1224,13%@1224,10%@1224] EMC_FREQ 0% GR3D_FREQ 0% PLL@21C CPU@25C PMIC@100C GPU@23.5C AO@33.5C thermal@24.5C POM_5V_IN 2545/2547 POM_5V_GPU 0/0 POM_5V_CPU 549/529
"""

"""
Tegrastats Notes:
RAM 5059/30623MB (lfb 5843x4MB) (lfb 5844x4MB)	5059 MB of RAM are in use, 30623 MB of RAM is available for applications and there are 5843 blocks of size 4 MB (the largest free block size or lfb) that can be allocated.
SWAP 0/15311MB (cached 0MB)	                    0 MB of SWAP used, 15311 MB of SWAP available for applications, and 0 MB of SWAP cached.
CPU [15%@735,...,8%@853]	                    Each A@B value is a statistic for one of the CPUs. The first CPU in the example has a load of 15% and is running at 735 MHz. The CPU load can also show as off if it's powered down.
EMC_FREQ 5%@3199	                            5% of the External Memory Controller bandwidth is used, and it's running at 3199 MHz.
GR3D_FREQ 0%@114	                            The first GPU engine has 0% of usage and is running at 114 MHz.
PLL@22C                                         ???
CPU@53.562C	                                    CPU with a temperature of 53.262 Celsius degrees.
PMIC@100C                                       ???
GPU@48.468C	                                    GPU with a temperature of 48.468 Celsius degrees.
AO@33C                                          ???
thermal@24.5C                                   ???
POM_5V_IN 2471/2819                             ???
POM_5V_GPU 0/0                                  ???
POM_5V_CPU 470/751                              ???
"""
