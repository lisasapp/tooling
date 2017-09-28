#!/bin/bash

cd $ASAPP_ROOT/tooling/srs_data
pythona -m get_model_observed_tags $1 $2
