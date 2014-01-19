#! /bin/bash

if [ -n "$1" ]; then
  identity=$1
else
  identity="protodo"
fi

#host_ip=37.139.29.18
host_ip=localhost

function post_etcd() {
  http PUT http://${host_ip}:4001/v2/keys/$identity/$1\?value=$2
  #curl -L -X POST http://${host_ip}:4001/v2/keys/$identity/$1 -d value="$2"
  sleep 1
}

post_etcd "universe" "nasdaq,4"
post_etcd "start" "2013-06-10"
post_etcd "end" "2014-01-10"

post_etcd "algorithm/save" "true"
#post_etcd "algorithm/notify" "true"
#post_etcd "algorithm/interactive" "true"
post_etcd "algorithm/long_window" "30"
post_etcd "algorithm/short_window" "20"
post_etcd "algorithm/threshold" "0.5"

post_etcd "manager/cash" "10020"

post_etcd "modules/algorithm" "insights.algorithms.buyandhold.BuyAndHold"
post_etcd "modules/manager" "insights.managers.fair.Fair"
post_etcd "modules/data" "insights.sources.backtest.yahoostock.YahooPriceSource"
