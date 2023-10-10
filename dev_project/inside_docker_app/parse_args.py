import re

class ArgumentParser():

    def __init__(self, args_list):
        self.args_list = args_list
        self.args_dict = self.get_dict_of_args()

    def get_dict_of_args(self):
        args_dict = {}
        all_flags_args_keys = re.findall(r"-[a-z]\s|-[a-z]$", " ".join(self.args_list))
        all_flags_args_keys = [arg.strip() for arg in all_flags_args_keys]
        all_key_args_keys = re.findall(r"--[a-z-_0-9]*", " ".join(self.args_list))
        all_key_args_keys = [arg.strip() for arg in all_key_args_keys]
        all_args_keys = all_flags_args_keys + all_key_args_keys
        current_index = 0
        while current_index < len(self.args_list):
            item = self.args_list[current_index]
            if current_index < len(self.args_list)-1 and item in all_args_keys and self.args_list[self.args_list.index(item) + 1] not in all_args_keys:
                args_dict[item] = self.args_list[self.args_list.index(item) + 1]
                current_index += 2
            else:
                args_dict[item] = True
                current_index += 1
        return args_dict