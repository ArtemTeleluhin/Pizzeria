class Product:
    def __init__(self, type_of_product, name, proportions, add_info=''):
        self.type_of_product = type_of_product
        self.name = name
        self.proportions = proportions
        self.add_info = add_info
        self.number_of_proportion = [0] * len(proportions)

    def set_proportion(self, proportion, val):
        self.number_of_proportion[proportion] = val

    def get_name(self):
        return self.name

    def get_add_info(self):
        return self.add_info

    def get_type(self):
        return self.type_of_product

    def get_proportion(self):
        return self.proportions

    def take_number_of_proportion(self, ind):
        return self.number_of_proportion[ind]
