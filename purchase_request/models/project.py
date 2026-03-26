from odoo import models, fields, api, exceptions
from datetime import datetime


class Project(models.Model):
    _name = 'pr.project.pae'
    _description = 'Project Management'
    _order = 'name'

    image = fields.Image('Image', attachment=True)  # แก้ตัวสะกด attachment
    name = fields.Char('Name', required=True)
    budget = fields.Float('Budget')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    type = fields.Selection([('N', 'Normal'), ('U', 'Urgent')], string='Type', default='N')
    department = fields.Char('Department')
    owner_id = fields.Many2one('res.users', string='Project Owner')

    # แก้ default ให้ส่งกลับเป็น String เพราะฟิลด์เป็น Char
    year = fields.Char(string='Year', default=lambda self: str(datetime.now().year))

    aging = fields.Integer(string='Aging', compute='get_project_aging', readonly=False, store=True)

    @api.depends('type', 'year')
    def get_project_aging(self):
        current_year = datetime.now().year
        for x in self:
            # เช็กก่อนว่า year มีค่าไหม และเป็นตัวเลขหรือเปล่า เพื่อกัน Error
            if x.year and x.year.isdigit():
                year_val = int(x.year)
                if x.type == 'N':
                    x.aging = (current_year - year_val) * 0.5
                elif x.type == 'U':
                    x.aging = (current_year - year_val) * 1.5
                else:
                    x.aging = 0
            else:
                x.aging = 0  # ถ้าไม่มีข้อมูลปี ให้ค่าเป็น 0 ไปก่อน