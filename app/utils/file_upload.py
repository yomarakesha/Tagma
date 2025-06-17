from wtforms import Field
from wtforms.widgets import FileInput

class FileUploadField(Field):
    widget = FileInput()

    def __init__(self, label=None, base_path=None, allowed_extensions=None, **kwargs):
        super().__init__(label, **kwargs)
        self.base_path = base_path
        self.allowed_extensions = allowed_extensions or set()

    def _value(self):
        return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = None

    def populate_obj(self, obj, name):
        pass  # Обработка в AdminView.on_model_change

class MultipleFileUploadField(FileUploadField):
    widget = FileInput(multiple=True)

    def process_formdata(self, valuelist):
        self.data = valuelist