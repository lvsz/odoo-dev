from odoo import api, models


@api.model
def _get(self, name):
    if res := self.name_search(name, limit=1):
        return self.browse(res[0][0])
    return self


class Base(models.AbstractModel):
    _inherit = 'base'

    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        if not hasattr(self, '_get'):
            setattr(self.__class__, '_get', _get)
