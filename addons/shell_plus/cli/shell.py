from odoo.api import attrsetter
from odoo.cli.shell import Shell


@attrsetter('_trans', str.maketrans({'_': ' ', '.': ' '}))
def model2var(name):
    return ''.join(name.translate(model2var._trans).title().split())


def extend_vars(env, local_vars):
    local_vars.update(
        commit=env.cr.commit,
        rollback=env.cr.rollback,
    )
    for model in env['ir.model'].search_fetch([], ['model']):
        local_vars[model2var(model.model)] = env[model.model]


@attrsetter('_orig', Shell.console)
def _patched_console(self, local_vars):
    if env := local_vars.get('env'):
        extend_vars(env, local_vars)
    try:
        return self.ipython(local_vars)
    except:  # noqa: E722
        __import__('ipdb').set_trace()
        return _patched_console._orig(self, local_vars)


Shell.console = _patched_console
