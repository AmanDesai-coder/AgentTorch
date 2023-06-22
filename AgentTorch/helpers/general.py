import re
from functools import reduce
import operator
import torch
import copy
from omegaconf import OmegaConf

def get_by_path(root, items):
    r"""
        Access a nested object in root by item sequence
    """
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    r"""
        Set a value in a nested object in root by item sequence
    """
    val_obj = get_by_path(root, items[:-1])
    val_obj[items[-1]] = value
    return root

def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]

def copy_module(dict_to_copy):
    r"""
        Creates a new dictionary with a copy of each PyTorch tensor in the input dictionary.
        Handles nested dictionaries of PyTorch tensors of variable depth.
    """
    copied_dict = {}
    for key, value in dict_to_copy.items():
        if torch.is_tensor(value):
            copied_dict[key] = torch.clone(value)
        elif isinstance(value, dict):
            copied_dict[key] = copy_module(value)
        elif not torch.is_tensor(value):
            copied_dict[key] = copy.deepcopy(value)
        else:
            raise TypeError("Type error.. ", type(value))
            
    return copied_dict

def process_shape(config, s):
    if type(s) == str:
        return get_by_path(config, re.split('/', s))
    else:
        return s

def read_config(config_file):
    # register OmegaConf resolvers for composite questions in OmegaConf
    OmegaConf.register_new_resolver("sum", lambda x, y: x + y)
    OmegaConf.register_new_resolver("multiply", lambda x, y: x*y)
    
    if config_file[-5:] != ".yaml":
        raise ValueError("Config file type should be yaml")
    try:
        config = OmegaConf.load(config_file)
        config = OmegaConf.to_object(config)
    except Exception as e:
        raise ValueError(f"Could not load config file. Please check path ad file type. Error message is {str(e)}")

    return config