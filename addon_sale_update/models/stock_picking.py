from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    wms_line_ids = fields.One2many('stock.wms', 'picking_id', string='WMS Lines')

    def action_create_wms_lines(self):
        for picking in self:
            wms_lines = []
            for move in picking.move_ids_without_package:
                product = move.product_id
                quantity = move.product_uom_qty

                vals = {
                    'picking_id': picking.id,
                    'name': picking.name,
                    'quantity': quantity,
                    'goods_type': picking.picking_type_id.code,  # optional
                    'status_wms': 'waiting plc'
                }

                # ใส่ barcode_in หรือ barcode_out ตามประเภท
                if picking.picking_type_id.code == 'incoming':  # รับเข้า
                    vals['barcode_in'] = product.barcode
                elif picking.picking_type_id.code == 'outgoing':  # ส่งออก
                    vals['barcode_out'] = product.barcode

                wms_lines.append((0, 0, vals))

            picking.wms_line_ids = wms_lines