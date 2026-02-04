try:
    from odoo.orm.decorators import attrsetter
except ImportError:
    from odoo.api import attrsetter
from odoo import fields
from odoo.cli.shell import Shell


@attrsetter('_trans', str.maketrans({'_': ' ', '.': ' '}))
def model2var(name):
    return ''.join(name.translate(model2var._trans).title().split())


def extend_vars(env, local_vars):
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
    for model in env['ir.model'].search_fetch([], ['model']):
        local_vars[model2var(model.model)] = env[model.model]


@attrsetter('_orig', Shell.console)
def _patched_console(self, local_vars):
    if env := local_vars.get('env'):
        extend_vars(env, local_vars)
    try:
        return self.ipython(local_vars)
    except:  # noqa: E722
        return _patched_console._orig(self, local_vars)


Shell.console = _patched_console
