# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU General Public License as published by           #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import osv, fields

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _description = "Picking List"

    _columns = {
                'fiscal_position': fields.many2one('account.fiscal.position', 'Posição Fiscal', domain="[('fiscal_operation_id','=',fiscal_operation_id)]"),
                }
    
    #TODO Fazer a dedução da operação e posição fiscal ao mudar o parceiro
    def onchange_partner_in(self, cr, uid, context=None, address_id=False, company_id=False):

        result = super(stock_picking, self).onchange_partner_in(cr, uid, context, address_id)
     
        if not company_id or not address_id:
            return result
        
        if not result:
            result = {'value': {'fiscal_position': False}}

        partner_addr = self.pool.get('res.partner.address').browse(cr, uid, address_id)
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid,  partner_addr.partner_id, address_id, company_id, context={'use_domain': ('use_picking','=',True)})
        
        result['value'].update(fiscal_result)
        
        return result


stock_picking()
