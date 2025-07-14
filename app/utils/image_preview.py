from wtforms import Field
from markupsafe import Markup
import json

class MultipleImagePreviewField(Field):
    def __init__(self, label='', validators=None, existing_images=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.existing_images = existing_images or []

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist
        else:
            self.data = []

    def __call__(self, **kwargs):
        html = ['<div style="max-height:150px;overflow:auto;border:1px solid #ccc;padding:5px">']
        for idx, img_url in enumerate(self.existing_images):
            html.append(f'''
                <div style="margin-bottom:5px">
                    <input type="checkbox" name="keep_image_{idx}" checked>
                    <img src="{img_url}" style="height:50px; vertical-align:middle; margin-right:10px;">
                    <input type="hidden" name="existing_image_{idx}" value="{img_url}">
                </div>
            ''')
        html.append('</div>')
        return Markup(''.join(html))
