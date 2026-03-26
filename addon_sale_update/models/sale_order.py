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



from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ###start proj lighup somchai modi 25-06-18
    qt_no = fields.Char('Quotations No', readonly=True, copy=False)
    sw_tax = fields.Selection([
        ('1', 'Goods'),
        ('2', 'Service'),

    ], string='Type Sale', default='1')

    @api.onchange('sw_tax')
    def _onchange_type_sale(self):
        """ Update tax in order lines based on type_sale """
        if self.sw_tax:
            tax_obj = self.env['account.tax']
            if self.sw_tax == '1':
                tax = tax_obj.search([('description', '=', 'SVAT01'), ('type_tax_use', '=', 'sale')], limit=1)
            else:
                tax = tax_obj.search([('description', '=', 'SVAT02'), ('type_tax_use', '=', 'sale')], limit=1)

            for line in self.order_line:
                line.tax_id = [(6, 0, [tax.id]) if tax else (5, 0, 0)]


    @api.model
    def create(self, vals):
        if not vals.get('qt_no'):
            vals['qt_no'] = self.env['ir.sequence'].next_by_code('sale.order.qtno') or '/'
        return super().create(vals)

    # @api.model
    # def create(self, vals):
    #      if 'qt_no' not in vals or vals.get('qt_no') == 0:
    #          last_qt = self.env['sale.order'].sudo().search([('qt_no', '!=', 0)], order='qt_no desc', limit=1)
    #         vals['qt_no'] = last_qt.qt_no + 1 if last_qt else 1
    #         return super().create(vals)

    ###end proj lighup somchai modi 25-06-18


    def action_confirm(self):
        # Call the super method to perform the default confirmation behavior
        res = super(SaleOrder, self).action_confirm()

        # Iterate through sale order lines to set the sdwht field based on product template
        for line in self.order_line:
            product_template = line.product_id.product_tmpl_id
            if product_template and product_template.wht:
                line.sdwht = product_template.wht

        return res

    def print_report_quations(self):
        self.ensure_one()
        so_no = self.name
        return {
            "type": "ir.actions.act_url",
            "url": "/web/binary/quations?so_no=%s" % (so_no),
            "target": "new",
        }
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
                # vals['sdwht'] = product_template.wht
                # vals['amtwht'] = vals['price_unit'] * vals['product_uom_qty'] * product_template.wht_per / 100
                vals['sdwht'] = False
                vals['amtwht'] = False
            else:
                vals['sdwht'] = False
                vals['amtwht'] = False
        else:
            # Default behavior if product_id is not provided
            vals['sdwht'] = False
            vals['amtwht'] = False

        # Call the super method to create the record
        return super(SaleOrderLine, self).create(vals)


# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = 'sale.advance.payment.inv'
#
#     def create_invoices(self):
#         # สร้างใบแจ้งหนี้จากคำสั่งขาย
#         # read sale_order header
#         # res = super()._create_invoices()
#
#         # หา Sale Orders จาก wizard
#         sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
#
#         # Loop ใบแจ้งหนี้ที่เพิ่งสร้างแล้วอัปเดต sw_tax
#         for order in sale_orders:
#             for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'draft'):
#                 invoice.sw_tax = order.sw_tax
#
#         # read sale_order line
#         invoices = self._create_invoices(self.sale_order_ids)
#
#         #### somchai modify sale to invoice pass parameter
#
#
#
#         for order in self.sale_order_ids:
#             for sale_line in order.order_line:
#                 # ค้นหา invoice ที่ถูกสร้างจากคำสั่งขาย
#                 for invoice in order.invoice_ids:
#                     for invoice_line in invoice.invoice_line_ids:
#                         if invoice_line.product_id == sale_line.product_id:
#                             # คัดลอกค่า sdwht และ amtwht จาก sale order line ไปที่ invoice line
#
#
#                             invoice_line.asdwht = sale_line.sdwht
#                             invoice_line.asdamtwht = sale_line.amtwht
#
#         # ส่ง invoice ที่เปิดถ้ามี
#         if self.env.context.get('open_invoices'):
#             return self.sale_order_ids.action_view_invoice()
#
#         return {'type': 'ir.actions.act_window_close'}

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        # ให้ Odoo สร้าง invoice ก่อน
        res = super()._create_invoices(sale_orders)

        # Loop ข้อมูล sale_order
        for order in sale_orders:
            for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'draft'):
                invoice.sw_tax = order.sw_tax

                # Loop sale_order_line → invoice_line
                for sale_line in order.order_line:
                    for invoice_line in invoice.invoice_line_ids:
                        if invoice_line.product_id == sale_line.product_id:
                            invoice_line.asdwht = sale_line.sdwht
                            invoice_line.asdamtwht = sale_line.amtwht

        return res

# ใน models/account_move.py

class AccountMove(models.Model):
    _inherit = 'account.move'

    sw_tax = fields.Selection([
        ('1', 'Goods'),
        ('2', 'Service'),
    ], string='Type Sale')

    sequentax = fields.Char(string='Invoice No.', copy=False, readonly=True)
    sequengood = fields.Char(string='เลขลำดับ สินค้า', copy=False, readonly=True)

    filtered_line_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='move_id',
        string='payment journal',
        compute='_compute_filtered_line_ids',
        store=False,
    )

    @api.depends('line_ids.journal_id')
    def _compute_filtered_line_ids(self):
        for move in self:
            # Check if the move has been paid; skip if not paid
            if move.payment_state != 'paid':
                # If not paid, skip further processing
                move.filtered_line_ids = self.env['account.move.line']
                continue

            # Search for the account.move record where the ref matches the current move name
            move_pay = self.env['account.move'].search([
                ('ref', '=', move.name)  # Match the ref with the name of the move
            ], limit=1)  # Limit to 1 to avoid multiple records

            pay_id = move_pay.id
            pay_doc = move.name

            if pay_id:
                # Execute raw SQL to update account.move.line
                # self.env.cr.execute("""
                # UPDATE account_move_line
                # SET
                #     account_id = CASE
                #                     WHEN journal_id = 6 THEN 36
                #                     WHEN journal_id = 9 THEN 4
                #                     WHEN journal_id = 7 THEN 37
                #                     ELSE account_id -- retain original if no condition is met
                #                  END,
                #     account_root_id = CASE
                #                         WHEN journal_id = 6 THEN 49049
                #                         WHEN journal_id = 9 THEN 49050
                #                         WHEN journal_id = 7 THEN 49050
                #                         ELSE account_root_id -- retain original if no condition is met
                #                       END
                # WHERE move_id = %s
                #  AND account_id not in (2,10)
                #    """, (pay_id,))

                # Update filtered_line_ids based on the criteria
                move.filtered_line_ids = self.env['account.move.line'].search([
                    ('move_id', '=', pay_id),  # Ensure move_id matches the current move
                    ('journal_id', 'in', [6, 7, 9, 5]),  # Only include lines with journal_id 6 or 7 or 9
                    # ('account_id', '!=', 2)  # Exclude lines with account_id 2
                ])
                #

            else:
                # If no matching move_pay found, assign an empty recordset
                move.filtered_line_ids = self.env['account.move.line']

    ################################################

    # @api.model
    # def create(self, vals):
    #
    #     if vals.get('move_type') == 'out_invoice' and not vals.get('name'):
    #         # หา sequence ที่ต้องการ
    #         seq_obj = self.env['ir.sequence'].search([('code', '=', 'account.move.custom_invoice_seq')], limit=1)
    #         if seq_obj:
    #             # เปลี่ยน prefix ชั่วคราวใน memory (ไม่กระทบ DB)
    #             prefix = f"{fields.Date.today().year}/"  # เช่น 2025/
    #             seq_obj = seq_obj.with_context(ir_sequence_date=fields.Date.today())
    #             seq_number = seq_obj._next(sequence_date=None, prefix=prefix)
    #             vals['name'] = seq_number
    #
    #     origin = vals.get('invoice_origin')  # → ถ้าไม่มี 'origin' จะได้ None
    #     # หรือถ้าแน่ใจว่าต้องมี origin เสมอ → ใช้ vals['origin']
    #     order_id = self.env['sale.order'].search([('name', '=', origin)], limit=1)
    #     chk_type = order_id.sw_tax
    #     if chk_type == '2':
    #         vals['sequentax'] = self.env['ir.sequence'].next_by_code('account.move.sequent') or '/'
    #     else:
    #         vals['sequentax'] = self.env['ir.sequence'].next_by_code('account.move.sequentgood') or '/'
    #
    #     return super().create(vals)



    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.name == '/':
                year = fields.Date.today().strftime('%Y')
                prefix = f"{year}/"
                seq = self.env['ir.sequence'].search([('code', '=', 'account.move')], limit=1)
                # if seq:
                #     move.name = seq.with_context(ir_sequence_prefix=prefix)._next()
                if move.sw_tax == '1':
                    move.name = "VT"+seq.with_context(ir_sequence_prefix=prefix)._next()

                else:
                    move.name = "SVT"+seq.with_context(ir_sequence_prefix=prefix)._next()
                self.tax_no = move.name
                self.sequentax = move.name
        # เรียกของเดิมต่อ
        return super().action_post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asdwht = fields.Boolean(string='ภาษีหัก ณ.ที่จ่าย')
    asdamtwht = fields.Float(string='ภาษีหักไว้')

    @api.model
    def create(self, vals):
        move_id = self.move_id
        acc_id = self.account_id
        print(acc_id)
        print(move_id)
        # เพิ่มค่าของ sdwht และ amtwht ถ้ามีใน context
        if self.env.context.get('from_sale_order'):
            sale_line = self.env['sale.order.line'].browse(self.env.context['sale_order_line_id'])
            vals['asdwht'] = sale_line.sdwht
            vals['asdamtwht'] = sale_line.amtwht

        return super(AccountMoveLine, self).create(vals)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Withholding Tax',
        domain=[('type_tax_use', '=', 'sale')],
        help="Select withholding tax to apply on this payment"
    )

    def action_create_payments(self):
        # 🔍 ทำอะไรบางอย่างก่อนสร้าง payment
        for wizard in self:
            if wizard.tax_id:
                print(f"[DEBUG] Selected WHT: {wizard.tax_id.name}")

        # 🔁 เรียกของเดิม (super)
        res = super().action_create_payments()

        # 🔧 ทำอะไรบางอย่างหลังจากสร้าง payment แล้ว
        # เช่น อัปเดต payment หรือสร้าง move line เพิ่ม ฯลฯ

        return res

class ProductTemplateMaster(models.Model):
    _inherit = "product.template"

    wht = fields.Boolean('ภาษีหัก ณ.ที่จ่าย')
    wht_per = fields.Integer('ภาษีหัก ณ.ที่จ่าย%')
    adv = fields.Boolean('หักเงินล่วงหน้า')
    adv_per = fields.Integer('หักเงินล่วงหน้าที่จ่าย%')

