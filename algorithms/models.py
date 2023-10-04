import base64
import io
import json

import numpy as np
import pydicom
from PIL import Image
from skimage import measure
from strawberry.file_uploads import Upload


class Queries:

    async def binarization(self, threshold: int, file: Upload) -> str:
        image = await file.read()
        dicom_dataset = pydicom.dcmread(io.BytesIO(image))

        # Convertir los píxeles DICOM a una matriz NumPy
        pixel_array = dicom_dataset.pixel_array

        binarized_array = pixel_array > threshold

        binarized_image = Image.fromarray((binarized_array * 255).astype(np.uint8))

        # Convertir la imagen en bytes
        image_stream = io.BytesIO()
        binarized_image.save(image_stream, format="PNG")
        image_data = image_stream.getvalue()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        return image_base64

    async def marching_squares(self, file: Upload) -> str:
        image = await file.read()
        ds = pydicom.dcmread(io.BytesIO(image))
        image = ds.pixel_array

        # Encuentra los contornos utilizando Marching Squares
        contours = measure.find_contours(image, 0.1, 'high')

        contours_np = [cont.astype(int) for cont in contours]
        serialized_contours = json.dumps([cont.tolist() for cont in contours_np])
        return serialized_contours