import json
# using json file as example
"""
{
    modules: {
        module: {setting: "setting_state"}
    },
    states: {
        chat1: {
            name1: {module: module_name, state: state_line},
            name2: {module: module_name, state: state_line},
        },
        chat2: {...}
    }
}
"""


class DB:
    def __init__(self, prefix=None):
        if prefix is not None:
            self.prefix = prefix + "_"
        else:
            self.prefix = ""
        self.db_file = "settings_db.json"
        self.init_db()
        return

    def init_db(self):
        try:
            open(self.db_file, "r")
        except FileNotFoundError:
            json.dump({"modules": {}, "states": {}}, open(self.db_file, "w"), indent=2)
        return

    def get_module_settings(self, module):
        all_settings = json.load(open(self.db_file, "r"))
        return all_settings["modules"][module]

    def get_setting(self, module, name):
        return self.get_module_settings(module)[name]

    def set_setting(self, module, name, state):
        all_settings = json.load(open(self.db_file, "r"))
        if module not in all_settings["modules"]:
            all_settings["modules"][module] = {}

        all_settings["modules"][module][name] = state
        json.dump(all_settings, open(self.db_file, "w"), indent=2)
        return

    def set_state(self, chat, user, module, state):
        all_settings = json.load(open(self.db_file, "r"))
        if chat not in all_settings["states"]:
            all_settings["states"][chat] = {}
        all_settings["states"][chat][user] = {"module": module, "state": state}
        json.dump(all_settings, open(self.db_file, "w"), indent=2)
        return

    def get_state(self, chat, user):
        chat = str(chat)
        user = str(user)
        all_settings = json.load(open(self.db_file, "r"))
        if chat in all_settings["states"]:
            if user in all_settings["states"][chat]:
                return all_settings["states"][chat][user]
        else:
            return None

    def clear_state(self, chat, user):
        chat = str(chat)
        user = str(user)
        all_settings = json.load(open(self.db_file, "r"))
        if chat not in all_settings["states"]:
            all_settings["states"][chat] = {}
        try:
            del all_settings["states"][chat][user]
        except KeyError:
            pass
        json.dump(all_settings, open(self.db_file, "w"), indent=2)
        return
