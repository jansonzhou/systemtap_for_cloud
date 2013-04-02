#!/bin/bash

host=10.1.83.83
systemtap_dir=/root/systemtap_dir
stp_file=$1

function mk_systemtap_dir () {
	ssh root@$host mkdir $systemtap_dir
}

function scp_stp () {
	#statements
	scp -r $1 root@$host:$systemtap_dir
}

function run_stp () {
	#statements
	ssh root@$host stap -v $systemtap_dir/$1
}

	//ssh root@$host stap -vp01 $systemtap_dir/$1
mk_systemtap_dir
scp_stp $stp_file
run_stp $stp_file


