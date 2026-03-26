# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, api, fields
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_confirm(self):
        # Call the super method to perform the default confirmation behavior
        res = super(PurchaseOrder, self).action_confirm()

        # Iterate through purchase order lines to set the sdwht field based on product template
        for line in self.order_line:
            product_template = line.product_id.product_tmpl_id
            if product_template and product_template.wht:
                line.sdwht = product_template.wht

        return res
    # create bill
    def action_create_invoice(self):
        # Create the bills using the existing process
        res = super(PurchaseOrder, self).action_create_invoice()

        # Debug: Ensure we are iterating over the correct objects
        _logger.info("Starting to map purchase lines to bill lines")

        for order in self:
            # Debug: Check purchase order lines
            _logger.info(f"Processing Purchase Order {order.name}, Lines: {order.order_line}")

            for purchase_line in order.order_line:
                # Debug: Log purchase line details
                _logger.info(f"Purchase Line {purchase_line.product_id.name}, SDWHT: {purchase_line.sdwht}, AMTWHT: {purchase_line.amtwht}")

                for bill in order.invoice_ids:
                    # Debug: Ensure the bill is created
                    _logger.info(f"Processing Bill {bill.name}")

                    # Check if a matching bill line exists
                    bill_line = bill.invoice_line_ids.filtered(lambda l: l.product_id == purchase_line.product_id)

                    if bill_line:
                        # If a matching bill line exists, update the fields
                        _logger.info(f"Matching Bill Line for Product: {bill_line.product_id.name}")
                        bill_line.asdwht = purchase_line.sdwht
                        bill_line.asdamtwht = purchase_line.amtwht
                        _logger.info(f"Updated SDWHT: {bill_line.asdwht}, AMTWHT: {bill_line.asdamtwht}")
                    else:
                        #####
                            ## Somchai  แก้ไข ลงบัญชี ข้าตั้งหนี้
                        #####

                        # pur_id = order.id
                        #
                        #
                        # pur_line_id = self.env['purchase.order.line'].search([
                        #     ('order_id', '=', pur_id) ,('sdwht', '=', False) # Match the ref with the name of the move
                        # ], limit=1)
                        # for line in pur_line_id:
                        #     acc_id = self.env['account.move.line'].search([
                        #         ('purchase_line_id', '=', line.id)  # Match the ref with the name of the move
                        #     ], limit=1)
                        #     print(acc_id)
                            ## ทำการ  update การลงบัญชี

                        # Create a new bill line if no matching product is found
                        _logger.info(f"No matching product for Bill Line. Creating a new line for {purchase_line.product_id.name}")
                        self.env['account.move.line'].create({
                            'move_id': bill.id,
                            'product_id': purchase_line.product_id.id,
                            'quantity': purchase_line.product_qty,
                            'price_unit': purchase_line.price_unit,
                            'asdwht': purchase_line.sdwht,
                            'asdamtwht': purchase_line.amtwht,
                        })
                        _logger.info(f"Created new Bill Line for Product: {purchase_line.product_id.name}, SDWHT: {purchase_line.sdwht}, AMTWHT: {purchase_line.amtwht}")

        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sdwht = fields.Boolean('ภาษีหัก ณ.ที่จ่าย')
    amtwht = fields.Float('ภาษีหักไว้')

    @api.model
    def create(self, vals):
        # Check if the product_id is in the vals and fetch the related product


        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals.get('product_id'))
            if product:
                product_template = product.product_tmpl_id
                # Set sdwht and amtwht based on the wht field in the product template
                vals['sdwht'] = product_template.wht
                vals['amtwht'] = vals['price_unit'] * vals['product_qty'] * product_template.wht_per / 100
            else:
                vals['sdwht'] = False
                vals['amtwht'] = False
        else:
            # Default behavior if product_id is not provided
            vals['sdwht'] = False
            vals['amtwht'] = False

        # Call the super method to create the record
        return super(PurchaseOrderLine, self).create(vals)






# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     asdwht = fields.Boolean(string='ภาษีหัก ณ.ที่จ่าย')
#     asdamtwht = fields.Float(string='ภาษีหักไว้')
#
#     @api.model
#     def create(self, vals):
#         # เพิ่มค่าของ sdwht และ amtwht ถ้ามีใน context จาก purchase order
#         if self.env.context.get('from_purchase_order'):
#             purchase_line = self.env['purchase.order.line'].browse(self.env.context['purchase_order_line_id'])
#             vals['asdwht'] = purchase_line.sdwht
#             vals['asdamtwht'] = purchase_line.amtwht
#
#         return super(AccountMoveLine, self).create(vals)
