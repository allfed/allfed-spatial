class Feature:

    def __init__(self, geom, data={}):
        self.geom = geom
        self.data = data

    def update_data(self, field, value):
        self.data[field] = value

    def update_length(self, unit='m'):
        if unit == 'm':
            length = max(self.geom.length, 1)
        elif unit == 'km':
            length = max(self.geom.length / 1000, 1)
        else:
            raise ValueError('Invalid unit')
        self.update_data('length', length)
