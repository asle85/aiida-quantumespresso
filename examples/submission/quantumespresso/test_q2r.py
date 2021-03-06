#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################

import sys
import os

from aiida.common.example_helpers import test_and_get_code
from aiida.orm import load_node

################################################################
UpfData = DataFactory('upf')
Dict = DataFactory('dict')
StructureData = DataFactory('structure')
try:
    dontsend = sys.argv[1]
    if dontsend == "--dont-send":
        submit_test = True
    elif dontsend == "--send":
        submit_test = False
    else:
        raise IndexError
except IndexError:
    print >> sys.stderr, ("The first parameter can only be either "
                          "--send or --dont-send")
    sys.exit(1)

try:
    parent_id = sys.argv[2]
    codename = sys.argv[3]
except IndexError:
    print >> sys.stderr, ("Must provide as further parameters the parent ID and "
                     "a q2r codename")
    sys.exit(1)

num_machines = 1 # node numbers
queue = None

#####
try:
    parent_id = int(parent_id)
except ValueError:
    print >> sys.stderr, 'Parent_id not an integer: {}'.format(parent_id)
    sys.exit(1)

code = test_and_get_code(codename, expected_code_type='quantumespresso.q2r')

computer = code.get_remote_computer()

parameters = Dict(dict={
            'INPUT': {
                'zasr': 'simple',
                },
            })

calc = code.new_calc(computer=computer)
calc.label = "Test QE q2r.x"
calc.description = "Test calculation with the Quantum ESPRESSO q2r.x code"
calc.set_option('max_wallclock_seconds', 60*30) # 30 min
calc.set_option('resources', {"num_machines":num_machines})

calc.use_parameters(parameters)
parentcalc = load_node(parent_id)
calc.use_parent_calculation(parentcalc)

if submit_test:
    subfolder, script_filename = calc.submit_test()
    print "Test_submit for calculation (uuid='{}')".format(
        calc.uuid)
    print "Submit file in {}".format(os.path.join(
        os.path.relpath(subfolder.abspath),
        script_filename
        ))
else:
    calc.store_all()
    print "created calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk)
    calc.submit()
    print "submitted calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk)
