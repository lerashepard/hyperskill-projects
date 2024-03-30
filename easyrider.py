import json


class BusCompany:

    data_types_match_dictionary = {
        "bus_id": {"type": int, "required": True},
        "stop_id": {"type": int, "required": True},
        "stop_name": {"type": str, "required": True},
        "next_stop": {"type": int, "required": True},
        "stop_type": {"type": "char", "required": False},
        "a_time": {"type": str, "required": True}
                            }

    mismatches = dict.fromkeys(data_types_match_dictionary, 0)

    def __init__(self, dict_data):
        self.dict_data = dict_data
        self.dict_data = json.loads(self.dict_data)

    def validate(self):
        for elem in self.dict_data:
            for key, value in elem.items():
                if value == "" and BusCompany.data_types_match_dictionary[key]["required"] == True:
                    BusCompany.mismatches[key] += 1
                else:
                    if type(value) != BusCompany.data_types_match_dictionary[key]["type"]:
                        if BusCompany.data_types_match_dictionary[key]["type"] != "char":
                            BusCompany.mismatches[key] += 1
                        else:
                            if type(value) != str:
                                BusCompany.mismatches[key] += 1
                            elif len(value) > 1:
                                BusCompany.mismatches[key] += 1

        sum_errors = sum([elem for elem in BusCompany.mismatches.values()])
        return BusCompany.mismatches, sum_errors

    def display_output(self):
        out_dict, error_sum = self.validate()
        print("Type and required fields validation: {} errors".format(error_sum))
        for key, value in out_dict.items():
            print("{}: {}".format(key, value))


input_dictionary = input()
EasyRider = BusCompany(input_dictionary)
EasyRider.display_output()
