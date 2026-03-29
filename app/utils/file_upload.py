from wtforms import Field, ValidationError
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
            if self.data and hasattr(self.data, 'filename') and self.data.filename and self.allowed_extensions:
                ext = self.data.filename.rsplit('.', 1)[-1].lower() if '.' in self.data.filename else ''
                if ext not in self.allowed_extensions:
                    raise ValidationError(f'File extension .{ext} is not allowed. Allowed: {", ".join(self.allowed_extensions)}')
        else:
            self.data = None

    def populate_obj(self, obj, name):
        pass  # Обработка в AdminView.on_model_change

class MultipleFileUploadField(FileUploadField):
    widget = FileInput(multiple=True)

    def process_formdata(self, valuelist):
        self.data = []
        for item in valuelist:
            if item and hasattr(item, 'filename') and item.filename and self.allowed_extensions:
                ext = item.filename.rsplit('.', 1)[-1].lower() if '.' in item.filename else ''
                if ext not in self.allowed_extensions:
                    raise ValidationError(f'File extension .{ext} is not allowed. Allowed: {", ".join(self.allowed_extensions)}')
            self.data.append(item)