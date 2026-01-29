from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get(self, name):
        if res := self.name_search(name, limit=1):
            return self.browse(res[0][0])
        return self
