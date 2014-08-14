# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo, Open Source Management Solution
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
from openerp.addons.program_purchase.program_result import prgs_cap


class program_result(orm.Model):

    _inherit = 'program.result'

    def _get_indicator_ids(self, cr, uid, ids, name, args, context=None):
        return {
            i['id']: i['result_indicator_ids']
            for i in self.read(
                cr, uid, ids, ['result_indicator_ids'], context=context)
        }

    def _get_prgs_realisation(self, cr, uid, ids, name, args, context=None):
        """Return realisation (capped between 0 and 100)"""
        if type(ids) is not list:
            ids = [ids]
        return {
            i['id']: prgs_cap(i['realisation']) for i in
            self.read(cr, uid, ids, ['realisation'], context=context)
        }

    _columns = {
        'result_indicator_ids2': fields.function(
            lambda self, *a, **kw: self._get_indicator_ids(*a, **kw),
            type="one2many",
            obj='program.result.indicator',
            string="Indicators",
            readonly=True,
        ),
        'realisation': fields.float(
            string='Realisation',
            track_visibility='onchange',
        ),
        'prgs_realisation': fields.function(
            lambda self, *a, **kw: self._get_prgs_realisation(*a, **kw),
            type='float',
            string='Realisation',
        ),
        'comment_realisation': fields.char(
            string='Comments',
            help='Comments for Realisation Progress',
        ),
    }