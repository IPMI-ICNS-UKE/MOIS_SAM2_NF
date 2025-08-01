import logging
import os
from typing import Dict

import monailabel
from monailabel.interfaces.app import MONAILabelApp
from monailabel.utils.others.class_utils import get_class_names
from monailabel.interfaces.config import TaskConfig
from monailabel.interfaces.datastore import Datastore
from monailabel.interfaces.tasks.infer_v2 import InferTask
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.interfaces.datastore import Datastore
import lib.configs

logger = logging.getLogger(__name__)


class NFSegmentationApp(MONAILabelApp):
    '''
     MONAI Label Application for Interactive Neurofibroma Segmentation in Whole-Body MRI.
     The app uses multi-object interactive segmentation SAM2 model (MOIS-SAM2) and operated in two modes:
        
        - Interactive segmentation based on user prompts (negative and positive points).
        - Automatic segmentation based on semantic propagation of already segmented lesions.
    '''
    def __init__(self, app_dir, studies, conf):
        self.model_dir = os.path.join(app_dir, "model")

        configs = {}
        for c in get_class_names(lib.configs, "TaskConfig"):
            name = c.split(".")[-2].lower()
            configs[name] = c

        configs = {k: v for k, v in sorted(configs.items())}
        
        # Load models from app model implementation, e.g., --conf models <segmentation_spleen>
        models = conf.get("models")
        if not models:
            print("")
            print("---------------------------------------------------------------------------------------")
            print("Provide --conf models <name>")
            print("Following are the available models.  You can pass comma (,) seperated names to pass multiple")
            print(f"    all, {', '.join(configs.keys())}")
            print("---------------------------------------------------------------------------------------")
            print("")
            exit(-1)

        models = models.split(",") if models else []
        models = [m.strip() for m in models]
        invalid = [m for m in models if m != "all" and not configs.get(m)]
        if invalid:
            print("")
            print("---------------------------------------------------------------------------------------")
            print(f"Invalid Model(s) are provided: {invalid}")
            print("Following are the available models.  You can pass comma (,) seperated names to pass multiple")
            print(f"    all, {', '.join(configs.keys())}")
            print("---------------------------------------------------------------------------------------")
            print("")
            exit(-1)
        
        self.planner = None 
         
        # app models
        self.models: Dict[str, TaskConfig] = {}
        for n in models:
            for k, v in configs.items():
                if self.models.get(k):
                    continue
                if n == k or n == "all":
                    logger.info(f"+++ Adding Model: {k} => {v}")
                    self.models[k] = eval(f"{v}()")
                    self.models[k].init(k, self.model_dir, conf, self.planner)
        logger.info(f"+++ Using Models: {list(self.models.keys())}")
        
        super().__init__(
            app_dir=app_dir,
            studies=studies,
            conf=conf,
            name=f"MONAILabel - NF Segmentation ({monailabel.__version__})",
            description="Pipeline for performing interactive NF segmentation on T2w WB-MRI scans",
            version=monailabel.__version__,
        )
    
    def init_datastore(self) -> Datastore:
        datastore = super().init_datastore()
        return datastore
    
    def init_infers(self) -> Dict[str, InferTask]:
        infers: Dict[str, InferTask] = {}
        for n, task_config in self.models.items():
            c = task_config.infer()
            c = c if isinstance(c, dict) else {n: c}
            for k, v in c.items():
                logger.info(f"+++ Adding Inferer:: {k} => {v}")
                infers[k] = v
        logger.info(infers)
        return infers
    
    def init_trainers(self) -> Dict[str, TrainTask]:
        trainers: Dict[str, TrainTask] = {}
        return trainers
    
    def infer(self, request, datastore=None):
        image_id = request["image"]
        
        if isinstance(image_id, str):
            datastore = datastore if datastore else self.datastore()
        
        label_id = datastore.get_label_by_image_id(image_id, tag="final")
        label = datastore.get_label_uri(label_id, label_tag="final")
        request["label_mask"] = label
        request["reset_state"] = True
        return super().infer(request, datastore)
