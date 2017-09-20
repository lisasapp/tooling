#!/bin/bash

# can create a python script to wrap this bash script that wraps python scripts..
BASELINE='20170828'
#RELEASE_SETS=('ComcastSRS-2.18.0' 'ComcastSRS-2.17.0' 'ComcastSRS-2.16.8' 'ComcastSRS-2.16.2' 'ComcastSRS-2.15.0' 'ComcastSRS-2.14.1' 'ComcastSRS-2.9.2' 'ComcastSRS-2.8.3' 'ComcastSRS-2.7.5' 'ComcastSRS-2.6.4')
#RELEASE_SETS=('ComcastSRS-2.18.0' 'ComcastSRS-2.14.1')
RELEASE_SETS=('ComcastSRS-2.18.0')

checkitout(){
    pushd $ASAPP_PRODML_ROOT
    git checkout $1
    popd
    pushd $ASAPP_SRS_ROOT
    #git checkout $1
    git checkout baselinereport
    popd
    pushd $ASAPP_COMCAST_SRS_ROOT
    git checkout $1
    popd
    pushd $ASAPP_MLENG_ROOT
    git checkout $1
    popd
}

echo baseline: $BASELINE
for release in "${RELEASE_SETS[@]}"; do
    # possibly need to checkout the most updated branch from each repo to load functions
    checkitout master

    # parse yaml to get args

    # call script to get model's observed data
    pythona -m get_model_observed_tags $release $BASELINE

    # get the latest mleng and stuff
    pushd $ASAPP_MLENG_ROOT
    git checkout master
    popd

    # generate excel metrics
    pythona -m evaluate_model $release $BASELINE

    #pid=$!
    #echo $pid
    #kill -9 $pid
done


