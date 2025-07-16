from wtforms import Field
from markupsafe import Markup

class MultipleImagePreviewField(Field):
    def __init__(self, label=None, validators=None, existing_images=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.existing_images = existing_images or []

    def _value(self):
        return ''

    def widget(self, field, **kwargs):
        html = ['<div style="display:flex; flex-wrap:wrap; gap:10px">']
        for image_url in self.existing_images:
            image_id = image_url.split("/")[-1]
            html.append(f'''
                <div style="position:relative;">
                    <img src="{image_url}" style="height:80px; border:1px solid #ccc;"/>
                    <a href="?remove_image={image_url}" style="position:absolute; top:0; right:0; background:#f00; color:#fff; padding:2px 5px; text-decoration:none;">×</a>
                </div>
            ''')
        html.append('</div>')
        return Markup(''.join(html))
