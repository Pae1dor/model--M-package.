# -*- coding: utf-8 -*-
from odoo import models, api, fields, osv
from odoo.exceptions import UserError,ValidationError
import datetime

class StockWMS(models.Model):
    _name = 'stock.wms'
    _rec_name = 'name'

    picking_id = fields.Many2one('stock.picking', string='Stock Picking')  # ฟิลด์ที่จำเป็น!
    name = fields.Char(string='เอกสารอ้างอิง')
    barcode_in = fields.Char(string='Barcode นำเข้า')
    barcode_out = fields.Char(string='Barcode ส่งออก')
    quantity = fields.Char(string='จำนวนสินค้า')
    goods_type = fields.Char(string='ประเภทสินค้า')
    status_wms = fields.Char(string='สถานะ wms')
    status_plc = fields.Char(string='สถานะ plc')
    channel_plc = fields.Char(string='ช่องเก็บของ')


