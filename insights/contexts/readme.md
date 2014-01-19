# Contexts

## API

```python
# (This is work in progress)
# A context provides at least this method signature
def build_context(storage):
    # The storage argument gives you informations to build the configuration
    context = {'end': '17h', 'universe': 'nasdaq,10'}
    strategy = {'algorithm': {'vwap': 15}, 'manager': {'sell': 0.3}}
    return context, strategy
```

* Then [Intuition][1] uses it with the following syntax:
``--context {{ context_type }}::{{ context_storage_argument }}``

* A minimal configuration looks like below. Every parameters wrote under
*algorithm* are available in ``TradingAlgorithm.init()`` with the
``properties`` dictionnary. An others under *manager* are accessible in the
``parameters`` dictionnary, given in __init__() and optimize() methods.

```yaml
universe: cac40,10
end: 17h
frequency: 1min
modules:
  manager: insights.managers.optimalfrontier.OptimalFrontier
  algorithm: insights.algorithms.gradient.StochasticGradientDescent
  data: insights.sources.live.EquitiesLiveSource
algorithm:
  save: true
  gradient_iterations: 5
manager:
  cash: 100000
```

## Library

### File

Simply provide the location of your yaml or json formated configuration file.

``--context file::path/to/file.{json,yaml,yml}``


### Mongodb

A configuration is stored as a [Mongodb][1] document. You must provide them
with an additional *id* information. Then you can use it with

``--context mongodb::{{ ip }}:{{ port }}/{{ doc_id }}``


### HTTP

The configuration is stored with [etcd][3] at v2/keys/{{ conf_id }}.

``--context etcd::{{ ip }}:{{ port }}/{{ conf_id }}``

To set a key / value :

```console
$ URL=http://{{ ip }}:{{ port }}/v2/keys/{{ conf_id }}
$ curl -L -XPUT $URL/universe -d value="nasdaq,5"
$ curl -L -XPUT $URL/{{ conf_id }}/algorithm/save -d value="true"
```


[1]: https://github.com/hackliff/intuition
[2]: mongodb.org
[3]: https://github.com/coreos/etcd
