from werkzeug.utils import secure_filename
import uuid as uuid

import os
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def img_to_uuid(img):
    fn = secure_filename(img.data.filename)
    img_id = str(uuid.uuid1()) + "_" + fn
    return img_id
