# Gaze in self-supervised learning
In the last work *Medical image supervised learning*, we use gaze to help computer aided diagnosis. However, CAM are usually used in supervised learning (with annotation).

In many cases, there are a lot of images that we have corresponding gaze but can not get the annotation.
We proposed **FocusContrast**:

```python
import torch
from PIL import Image
import numpy as np
import cv2 as cv
from torchvision import transforms
from typing import Callable, List, Tuple

CONFIG_ZOOMIN = 2
CONFIG_DEGREE = 45
CONFIG_CUTOUT = 48 

def decouple_to_numpy(pil_img: Image) -> np.array:
    """ This function returns the img and the saliency which are all
        SINGLE channel grayscale

    Args:
        pil_img ([type]): [special made for openselfsup]

    Returns:
        np.array: [img, 0-1 float], np.array: [img, 0-1 np.float32]
    """

    np_input = np.array(pil_img, dtype=np.uint8)
    np_img = np_input[:, :, 0]/255
    np_saliency = np_input[:, :, 1]/255
    return np_img.astype(np.float32), np_saliency.astype(np.float32)


def prob_wrapper(transform_function: Callable, p: float = 1.0) -> Callable:
    def prob_transform_func(img: np.array, saliency: np.array, *args, **kwargs):
        rand_01 = np.random.random()
        if rand_01 < p:
            img, saliency = transform_function(img, saliency, *args, **kwargs)
        return img, saliency
    return prob_transform_func


def compose(list_of_transforms: list) -> Callable:
    """
    returns composed transform function which have a special input image of
    three channel: [grayscale_org_img, saliency, zeros]

    Args:
        list_of_transforms (list): [list of transform in Operator and FocusContrastOperator]

    Returns:
        function: [composed transform, input is a pil image]
    """
    def composed_transforms(img, saliency):
        for transform_func in list_of_transforms:
            img, saliency = transform_func(img, saliency)
        return img, saliency
    return composed_transforms


def pipeline(transforms_and_probs: List[Tuple[Callable, float]]) -> Callable:
    """ Returns the entire process pipeline function
        that have a input of pil image and have a output of tensor

    Args:
        transforms_and_probs (List[Callable, float]): [()]

    Returns:
        Callable: [description]
    """
    prob_transform_func = []
    for transform_func, p in transforms_and_probs:
        prob_transform_func.append(prob_wrapper(transform_func, p))
    composed_func = compose(prob_transform_func)

    def inner(pil_img: Image) -> torch.tensor:
        img, saliency = decouple_to_numpy(pil_img)
        img, saliency = composed_func(img, saliency)
        return torch.from_numpy(img.astype(np.float32))
    return inner


def torch_function_for_numpy(torch_func: Callable) -> Callable:
    """ This function turns a
        torch.tensor->torch.tensor function to np.array->np.array function

    Args:
        torch_func (function): [torch.tensor->torch.tensor]

    Raises:
        TypeError: [only support 0.0-1.0 image]

    Returns:
        function: [np.array->np.array]
    """
    ''' This function turns a
        torch.tensor->torch.tensor function to np.array->array function
    '''
    def numpy_func(np_img: np.array):
        assert (np_img.dtype == np.float32 and np.max(np_img) <=
                1 and np.min(np_img) >= 0), "image has to be 0-1 and np.float32"
        torch_img = torch.from_numpy(np_img)
        torch_result = torch_func(torch_img)
        np_result = torch_result.numpy()
        return np_result
    return numpy_func


def same_random_transform_on_both(img: np.array, saliency: np.array, np_random_transform: Callable) -> np.array:
    """ Perform transform function (np.array->np.array) on two np image (both 0-1 and 0-255 are supported)

    Args:
        img (np.array): [0-1 np.array]
        saliency (np.array): [0-1 np.array]
        np_random_transform (function): [np.array->np.array]

    Returns:
        np.array: [transformed img and saliency]
    """
    w, h = img.shape
    coupled_input = np.zeros(shape=(3, w, h), dtype=np.float32)
    coupled_input[0, :, :] = img
    coupled_input[1, :, :] = saliency
    result = np_random_transform(coupled_input)
    result_img = result[0]
    result_saliency = result[1]
    return result_img, result_saliency


class Operator:
    """ Augmentation operators that are not work with saliency or any other information
    """
    # config = {'degree':}

    @ staticmethod
    def color_distort(img: np.array, saliency: np.array) -> np.array:
        torch_color_distort = transforms.ColorJitter(
            brightness=0.2, contrast=0.8)
        numpy_color_distort = torch_function_for_numpy(torch_color_distort)
        # we need a three channel channel first
        img = np.array([img, img, img])
        result = numpy_color_distort(img)
        return result[0], saliency

    @ staticmethod
    def random_flip(img, saliency) -> np.array:
        torch_random_flip = transforms.RandomHorizontalFlip()
        numpy_random_flip = torch_function_for_numpy(torch_random_flip)
        result_img, result_saliency = same_random_transform_on_both(
            img, saliency, numpy_random_flip)
        return result_img, result_saliency

    @ staticmethod
    def random_rotate(img, saliency) -> np.array:
        torch_random_rotate = transforms.RandomRotation(degrees=CONFIG_DEGREE)
        numpy_random_rotate = torch_function_for_numpy(torch_random_rotate)
        result_img, result_saliency = same_random_transform_on_both(
            img, saliency, numpy_random_rotate)
        return result_img, result_saliency

    @ staticmethod
    def random_crop(img, saliency) -> np.array:
        zoom_in_ratio = (CONFIG_ZOOMIN-1.2) * np.random.rand(1) + 1.2
        w, h = img.shape
        new_w, new_h = int(w*zoom_in_ratio), int(h*zoom_in_ratio)
        new_img = cv.resize(img, dsize=(new_w, new_h))
        new_saliency = cv.resize(saliency, dsize=(new_w, new_h))

        p = (np.random.randint(low=0, high=new_w-w),
             np.random.randint(low=0, high=new_h-h))

        cropped_img = new_img[p[0]:p[0]+w, p[1]:p[1]+h]
        cropped_saliency = new_saliency[p[0]:p[0]+w, p[1]:p[1]+h]
        return cropped_img, cropped_saliency

    @ staticmethod
    def random_cutout(img, saliency, minimal_size=32) -> np.array:
        minimal_size = CONFIG_CUTOUT
        w, h = img.shape
        canvas = np.zeros(img.shape)
        pt1 = (np.random.randint(low=0, high=w-minimal_size),
               np.random.randint(low=0, high=h-minimal_size))
        # pt2 = (pt1[0]+minimal_size, pt1[1]+minimal_size)
        pt2 = (np.random.randint(low=pt1[0]+minimal_size, high=w),
               np.random.randint(low=pt1[1]+minimal_size, high=h))
        mask = cv.rectangle(canvas, pt1, pt2, color=1.0,
                            thickness=cv.FILLED)

        result = np.multiply(1-mask, img)
        return result, saliency

    @ staticmethod
    def reshape(img, saliency, target_shape=(224,224)) -> np.array:
        new_img = cv.resize(img, dsize=target_shape)
        new_saliency = cv.resize(saliency, dsize=target_shape)
        return new_img, new_saliency
    
    @ staticmethod
    def to_RGB(img, saliency) -> np.array:
        if len(img.shape)==2:
            img = np.stack([img,img,img])
        if len(saliency.shape)==2:
            saliency = np.stack([saliency,saliency,saliency])
        return img, saliency

class FocusContrastOperator:
    """ Augmentation operator with focus/saliency
    """
    @ staticmethod
    def focus_drop(img, saliency, drop_to=0.1) -> np.array:
        # make this 0-1
        saliency = cv.GaussianBlur(saliency, (199, 199), 0)
        saliency = saliency/(0.01+np.max(saliency))
        # add non-saliece-value to make the image not entirely black
        saliency += drop_to
        saliency = np.clip(saliency, 0, 1)
        result = np.multiply(img, saliency)
        return result, saliency

    @ staticmethod
    def focus_crop(img, saliency, threshold=0.9, zoom_in_ratio=CONFIG_ZOOMIN) -> np.array:
        w, h = img.shape
        zoom_in_ratio = (zoom_in_ratio-1) * np.random.rand(1) + 1 # 1-zoom_in_ratio
        new_w, new_h = int(w*zoom_in_ratio), int(h*zoom_in_ratio)
        new_img = cv.resize(img, dsize=(new_w, new_h))
        new_saliency = cv.resize(saliency, dsize=(
            new_w, new_h), interpolation=cv.INTER_NEAREST)

        def get_new_pt1():
            pt1 = (np.random.randint(low=0, high=new_w-w),
                   np.random.randint(low=0, high=new_h-h))
            return pt1

        rand_pt1 = get_new_pt1()
        saliency_crop = new_saliency[rand_pt1[0]:rand_pt1[0]+w,
                                     rand_pt1[1]:rand_pt1[1]+h]
        saliency_ratio = np.sum(saliency_crop) / \
            (np.sum(saliency)+1e-4)/(zoom_in_ratio**2)
        # if the generated crop have too little overlap with the saliency, desprecate it
        # and generate a new mask until it passes.
        counter = 0
        while(saliency_ratio < threshold and counter < 200):
            rand_pt1 = get_new_pt1()
            saliency_crop = new_saliency[rand_pt1[0]:rand_pt1[0]+w,
                                         rand_pt1[1]:rand_pt1[1]+h]
            saliency_ratio = np.sum(saliency_crop) / \
                (np.sum(saliency)+1e-4)/(zoom_in_ratio**2)
            # print(saliency_ratio)
            counter += 1

        cropped_img = new_img[rand_pt1[0]:rand_pt1[0]+w,
                              rand_pt1[1]:rand_pt1[1]+h]
        cropped_saliency = new_saliency[rand_pt1[0]:rand_pt1[0]+w,
                                        rand_pt1[1]:rand_pt1[1]+h]
        return cropped_img, cropped_saliency

    @ staticmethod
    def focus_cutout(img, saliency, threshold=400, minimal_size=CONFIG_CUTOUT) -> np.array:
        w, h = img.shape

        def get_new_cutoutmask():
            canvas = np.zeros(img.shape)
            pt1 = (np.random.randint(low=0, high=w-minimal_size),
                   np.random.randint(low=0, high=h-minimal_size))
            # pt2 = (pt1[0]+minimal_size, pt1[1]+minimal_size)
            pt2 = (np.random.randint(low=pt1[0]+minimal_size, high=w),
                   np.random.randint(low=pt1[1]+minimal_size, high=h))
            mask = cv.rectangle(canvas, pt1, pt2, color=1.0,
                                thickness=cv.FILLED)
            return mask
        rand_mask = get_new_cutoutmask()
        # if the generated mask have too much overlap with the saliency, desprecate it
        # and generate a new mask until it passes.
        overlap = np.sum(rand_mask*saliency)
        # print("overlap is:", overlap)
        counter = 0
        while(overlap > threshold and counter < 100):
            rand_mask = get_new_cutoutmask()
            overlap = np.sum(rand_mask*saliency)
            counter += 1
        result = np.multiply(1-rand_mask, img)
        return result, saliency
```