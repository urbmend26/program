# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class program_result_level(orm.Model):

    _inherit = 'program.result.level'
    _columns = {
        'top_level_menu': fields.boolean('Has Top Level Menu'),
        'top_level_menu_name': fields.char('Top Level Menu Name'),
        # 'top_level_menu_id': fields.many2one('Top Level Menu'),
    }

    def validate_vals(self, vals):
        top_level_menu = vals.get('top_level_menu')
        if top_level_menu is False:
            vals['top_level_menu_name'] = False
        top_level_menu_name = vals.get('top_level_menu_name')
        parent_id = vals.get('parent_id')

        if top_level_menu and not top_level_menu_name:
            raise orm.except_orm(
                _('Error!'),
                _('No Menu Name provided')
            )

        if parent_id and top_level_menu:
            raise orm.except_orm(
                _('Error!'),
                _('Top level menus can only be set on the highest level '
                  'of a result chain')
            )

    def create(self, cr, user, vals, context=None):
        self.validate_vals(vals)

        return super(program_result_level, self).create(
            cr, user, vals, context=context
        )

    def write(self, cr, user, ids, vals, context=None):
        """Bubble up Top Menu configuration if chain root changes"""
        if isinstance(ids, (int, long)):
            ids = [ids]

        self.validate_vals(vals)
        top_level_menu = vals.get('top_level_menu')

        for level in self.browse(cr, user, ids, context=context):
            if (vals.get('parent_id') is not False
                    and level.depth > 1
                    and top_level_menu):
                raise orm.except_orm(
                    _('Error!'),
                    _('Top level menus can only be set on the highest level '
                      'of a result chain')
                )

        res = super(program_result_level, self).write(
            cr, user, ids, vals, context=context
        )

        if 'parent_id' in vals:
            self._bubble_up_menu(cr, user, ids, context=context)

        return res

    def _bubble_up_menu(self, cr, user, ids, context=None):
        """Bubble up Top Menu configuration to root of chain"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        for level in self.browse(cr, user, ids, context=context):
            if not level.parent_id or not level.top_level_menu:
                continue
            top_level_menu = level.top_level_menu
            top_level_menu_name = level.top_level_menu_name
            level.write({
                'top_level_menu': False,
                'top_level_menu_name': False,
            })
            root = level.chain_root
            if not root.top_level_menu:
                root.write({
                    'top_level_menu': top_level_menu,
                    'top_level_menu_name': top_level_menu_name,
                })
