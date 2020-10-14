import tensorflow as tf
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image, resize_image
from enum import Enum
import os

class InferTypeEnum(Enum):
    cpu = 0
    gpu = 1
    open_vino_cpu = 2

class MlConfig:
    weights: str = None
    min_side: int = None
    max_side: int = None
    backbone: str = None
    labels: dict = None
    infer_type: InferTypeEnum = InferTypeEnum.cpu
    alias: str

    def __init__(self, alias: str):
        self.alias = alias

class Model:
    config: MlConfig

    def __init__(self, config: MlConfig) -> None:
        assert os.path.isfile(config.weights), f"no such file: {config.weights}"
        assert config.backbone != None, "backbone is None"
        assert config.labels != None, "labels is none"
        self.config = config
        self.model = None
    
    def load(self) -> None:
        if self.config.infer_type == InferTypeEnum.gpu:
            self._setup_gpu(1)
        elif self.config.infer_type == InferTypeEnum.cpu:
            self._setup_gpu(-1)
        else:
            raise Exception(f"unsuported infer_type {self.config.infer_type}")

        self.model = models.load_model(args.model, backbone_name=self.config.backbone)

    def infer(self, in_data: bytes) -> dict:
        # pre-processing
        img_bytes = np.asarray(bytearray(in_data), dtype=np.uint8)
        image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
        image, scale = resize_image(image, min_side=self.config.min_side, max_side=self.config.min_side)
        image = preprocess_image(image)
        
        # inference
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(image, axis=0))
        
        # post-processing
        boxes /= scale
        objects = []
        result = {
            'objects': objects
        }
        for box, _, label in zip(boxes[0], scores[0], labels[0]):
            if score < 0.5:
                break
            b = np.array(box.astype(int)).astype(int)
            # x1 y1 x2 y2
            obj = {
                'label': self.config.labels[label],
                'xmin': b[0],
                'ymin': b[1],
                'xmax': b[2],
                'ymax': b[3]
            }
            objects.append(obj)
        return result


    def _setup_gpu(self, gpu_id: int) -> None:
        if gpu_id == -1:
            tf.config.experimental.set_visible_devices([], 'GPU')
            return

        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                tf.config.experimental.set_virtual_device_configuration(
                    gpus[gpu_id],
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                raise Exception(f"unable to setup gpu: {e}")



        
    