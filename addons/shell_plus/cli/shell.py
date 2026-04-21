from contextlib import suppress

try:
    from odoo.orm.decorators import attrsetter
except ImportError:
    from odoo.api import attrsetter
from odoo import api, fields
from odoo.cli.shell import Shell


class LocalEnv:
    def __init__(self, default=None):
        if default is None:
            return
        self.models = LocalEnv()
        self._default = LocalEnv()
        for key, value in default.items():
            setattr(self._default, key, value)


@api.model
def _get(self, name, op='ilike', fname=None, limit=1):
    if fname in (None, self._rec_name):
        if res := self.name_search(name, operator=op, limit=limit):
            return self.browse(x[0] for x in res)
    if fname in self._fields or (fname := next((
        field for field, values in self.fields_get([], ['selection']).items()
        if any(name == sel[0] for sel in values.get('selection', []))
    ), None)):
        return self.search([(fname, op, name)], limit=limit)
    return self


@attrsetter('_trans', str.maketrans({'_': ' ', '.': ' '}))
def model2var(name):
    return ''.join(name.translate(model2var._trans).title().split())


def extend_vars(env, local_vars):
    local_env = LocalEnv(default=local_vars)
    local_vars.update(
        commit=env.cr.commit,
        rollback=env.cr.rollback,
        admin=env.ref('base.user_admin'),
        demo=env.ref('base.user_demo', raise_if_not_found=False) or env['res.users'],
        eur=env.ref('base.EUR'),
        usd=env.ref('base.USD'),
        Command=fields.Command,
        Date=fields.Date,
        Datetime=fields.Datetime,
        timedelta=__import__('datetime').timedelta,
        defaultdict=__import__('collections').defaultdict,
    )
    if hasattr(fields, 'Domain'):
        local_vars['Domain'] = fields.Domain
    with suppress(ModuleNotFoundError):
        ipdb = __import__('ipdb')
        local_vars.update(ipbd=ipdb, set_trace=ipdb.set_trace)
    for key, value in local_vars.items():
        setattr(local_env, key, value)
    for ir_model in env['ir.model'].search_fetch([], ['model']):
        model_name = model2var(ir_model.model)
        local_vars[model_name] = model = env[ir_model.model]
        setattr(local_env.models, model_name, model)
        if not hasattr(model.__class__, '_get'):
            setattr(model.__class__, '_get', _get)
    local_vars['_env'] = local_env


@attrsetter('_orig', Shell.console)
def _patched_console(self, local_vars):
    if env := local_vars.get('env'):
        extend_vars(env, local_vars)
    with suppress(Exception):
        return self.ipython(local_vars)
    return _patched_console._orig(self, local_vars)


Shell.console = _patched_console
