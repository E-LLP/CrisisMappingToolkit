import logging
logging.basicConfig(level=logging.ERROR)
import util.ee_authenticate
util.ee_authenticate.initialize()
import matplotlib
matplotlib.use('tkagg')

import os
import ee
import functools

import modis.domains
from modis.flood_algorithms import *

from util.mapclient_qt import centerMap, addToMap
from util.evaluation   import evaluate_approach

# --------------------------------------------------------------
# Configuration

# Specify the data set to use - see /modis/domains.py
DOMAIN = modis.domains.BORDER

# Specify each algorithm to be concurrently run on the data set - see /modis/flood_algorithms.py
ALGORITHMS = [DARTMOUTH, DIFFERENCE, DNNS, DNNS_DEM]


# --------------------------------------------------------------
# Functions

def evaluation_function(pair, alg):
    '''Pretty print an algorithm and its statistics'''
    precision, recall = pair
    print '%s: (%4g, %4g)' % (get_algorithm_name(alg), precision, recall)


# --------------------------------------------------------------
# main()

# Fetch data set information
d = modis.domains.retrieve_domain(DOMAIN)

# Display the Landsat and MODIS data for the data set
centerMap(d.center[0], d.center[1], 11)
addToMap(d.landsat,       {'bands': ['B3', 'B2', 'B1'], 'gain': d.landsat_gain}, 'Landsat RGB')
addToMap(d.low_res_modis, {'bands': ['sur_refl_b01', 'sur_refl_b02', 'sur_refl_b06'], 'min' : 0, 'max': 3000, 'opacity' : 1.0}, 'MODIS', False)

addToMap(d.ground_truth.mask(d.ground_truth), {'min': 0, 'max': 1, 'opacity': 0.5}, 'Ground Truth', False)

# For each of the algorithms
for a in range(len(ALGORITHMS)):
    # Run the algorithm on the data and get the results
    (alg, result) = detect_flood(d, ALGORITHMS[a])

    # Get a color pre-associated with the algorithm, then draw it on the map
    color = get_algorithm_color(ALGORITHMS[a])
    addToMap(result.mask(result), {'min': 0, 'max': 1, 'opacity': 0.5, 'palette': '000000, ' + color}, alg, False)

    # Compare the algorithm output to the ground truth and print the results
    evaluate_approach(functools.partial(evaluation_function, alg=ALGORITHMS[a]), result, d.ground_truth, d.bounds, is_algorithm_fractional(ALGORITHMS[a]))

#addToMap(domain.groundTruth.mask(domain.groundTruth), {'min': 0, 'max' : 1, 'opacity' : 0.2}, 'Ground Truth', false);
#addToMap(domain.dem, {min:25, max:50}, 'DEM', false);










