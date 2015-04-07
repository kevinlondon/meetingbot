import yaml
from .utils import memoize


@memoize
def load(filename="config.yaml"):
    with open(filename, 'r') as yamlconf:
        config = yaml.safe_load(yamlconf)

    return config
