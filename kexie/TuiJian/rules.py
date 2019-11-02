# rules.py
# On Python 2, you must also add the following to the top of your rules.py file, or you'll get import errors trying to import django-rules itself
from __future__ import absolute_import

import rules

# 使用修饰符@rules.predicate自定义predicates（判断），返回True表示有权限，False表示无权限

# Predicates

@rules.predicate
def is_colleague(user, entry):
    if not entry or not hasattr(user, 'controlqgxh'):
        return False
    return entry.source == user.controlqgxh.source
@rules.predicate
def is_admin(user):
    if not hasattr(user, 'controlqgxh'):
        return False
    return user.controlqgxh.is_admin


is_colleague_or_admin = (is_colleague or rules.is_superuser or is_admin)

# 设置Rules

rules.add_rule('can_view_qgxh', is_colleague_or_admin)
rules.add_rule('can_delete_qgxh', is_colleague_or_admin)
rules.add_perm('can_change_qgxh', is_colleague_or_admin)
rules.add_perm('can_add_qgxh', is_colleague_or_admin)
# 设置Permissions

rules.add_perm('data_import.view_qgxh', is_colleague_or_admin)
rules.add_perm('data_import.delete_qgxh', is_colleague_or_admin)
rules.add_perm('data_import.add_qgxh', is_colleague_or_admin)
rules.add_perm('data_import.change_qgxh', is_colleague_or_admin)



@rules.predicate
def is_dfkx_colleague(user, entry):
    if not entry or not hasattr(user, 'controldfkx'):
        return False
    return entry.source == user.controldfkx.source
@rules.predicate
def is_dfkx_admin(user):
    if not hasattr(user, 'controldfkx'):
        return False
    return user.controldfkx.is_admin


is_dfkx_colleague_or_admin = (is_dfkx_colleague or rules.is_superuser or is_dfkx_admin)

# 设置Rules

rules.add_rule('can_view_dfkx', is_dfkx_colleague_or_admin)
rules.add_rule('can_delete_dfkx', is_dfkx_colleague_or_admin)
rules.add_perm('can_change_dfkx', is_dfkx_colleague_or_admin)
rules.add_perm('can_add_dfkx', is_dfkx_colleague_or_admin)
# 设置Permissions

rules.add_perm('data_import.view_dfkx', is_dfkx_colleague_or_admin)
rules.add_perm('data_import.delete_dfkx', is_dfkx_colleague_or_admin)
rules.add_perm('data_import.add_dfkx', is_dfkx_colleague_or_admin)
rules.add_perm('data_import.change_dfkx', is_dfkx_colleague_or_admin)