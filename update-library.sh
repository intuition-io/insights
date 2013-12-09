#! /bin/bash
#
# update_library.sh
# Copyright (C) 2013 Xavier Bruhiere

# const (
algorithmic_path="$PWD"
data_path="$PWD/sources"
LIBRARY="library.py"
# )

#contrib_index=( "algorithms" "managers")
contrib_index=()
contrib_index+=("$algorithmic_path/algorithms")
contrib_index+=("$algorithmic_path/managers")
contrib_index+=("$data_path/backtest")
contrib_index+=("$data_path/live")


algos_dict="algorithms = {"
managers_dict="portfolio_managers = {"
sources_dict="data_sources = {"
imports=""


for path in ${contrib_index[@]}; do
  while IFS=' ' read -ra ADDR; do
    for file in "${ADDR[@]}"; do
      #TODO Something more elegant...
      if [[ "$file" != *"__init__"* ]]; then

        class_names=$(cat $file | grep "^class" | \
          awk -F " " '{print $2}' | \
          awk -F "(" '{if (($2 == "TradingAlgorithm):")  || ($2 == "TradingFactory):") || ($2 == "PortfolioFactory):") || ($2 == "DataFactory):")) print $1}')

        if [[ $class_names == "" ]]; then
          continue
        fi

        for class in ${class_names}; do
          if [[ $path == *"managers"* ]]; then
            echo "adding manager $class to library"
            managers_dict+="'$class': $class,"
          elif [[ $path == *"algorithms"* ]]; then
            echo "adding algorithm $class to library"
            algos_dict+="'$class': $class,"
          elif [[ $path == *"sources"* ]]; then
            echo "adding data source $class to library"
            sources_dict+="'$class': $class,"
          fi
        done

        class_names=$(echo $class_names | tr " " ", ")
        file_path=$(echo $file | tr "/" "." | awk -F "intuition" \
          '{print "intuition"$3}' | awk -F ".py" '{print $1}')
        imports+="from $file_path import $class_names"
        imports+="-"
      fi
    done
  done <<< "$(ls $path/*.py)"
done

algos_dict+="}"
managers_dict+="}"
sources_dict+="}"

echo "#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# !!
# This file has been automatically generated
# Don't edit it manually, use update-library.sh script instead
# !!


import logbook


log = logbook.Logger('intuition.library')

" > "${LIBRARY}"

echo $imports | tr "-" "\n" >> "${LIBRARY}"
echo -e "\n$algos_dict" >> "${LIBRARY}"
echo -e "\n$managers_dict" >> "${LIBRARY}"
echo -e "\n$sources_dict" >> "${LIBRARY}"
echo "

#TODO optimization algos

def check_availability(algo, manager, source):
  if algo not in algorithms:
    raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
  log.debug('Algorithm {} available, getting a reference on it.'.format(algo))

  if (manager) and (manager not in portfolio_managers):
    raise NotImplementedError('Manager {} not available or implemented'.format(manager))
  log.debug('Manager {} available, getting a reference on it.'.format(manager))

  if (source) and (source not in data_sources):
    raise NotImplementedError('Source {} not available or implemented'.format(source))
  log.debug('Source {} available'.format(source))

  return True" >> "${LIBRARY}"
