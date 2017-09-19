#!/bin/bash

BASELINE='20170828'
#MODEL_SETS=('ComcastSRS-2.18.0' 'ComcastSRS-2.17.0' 'ComcastSRS-2.16.8' 'ComcastSRS-2.16.2' 'ComcastSRS-2.15.0' 'ComcastSRS-2.14.1' 'ComcastSRS-2.9.2' 'ComcastSRS-2.8.3' 'ComcastSRS-2.7.5' 'ComcastSRS-2.6.4')
MODEL_SETS=('ComcastSRS-2.18.0' 'ComcastSRS-2.14.1')
#MODEL_SETS=('ComcastSRS-2.18.0')

echo baseline: $BASELINE
for model in "${MODEL_SETS[@]}"; do
    pythona -m get_model_observed_tags $model
    #pid=$!
    #echo $pid
    #kill -9 $pid
done


