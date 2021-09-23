# Deep learning examples
In this page, we introduce how to utilize the collected gaze in deep learning tasks. Here we introduce two "static heatmap" methods, which means we do not take the order of the gaze into consideration.

## Human attention guide network attention

We implement a simple yet effective deep learning solution for utilizing the guidance from the radiologist’s gaze. We demonstrate that the extra supervision from expert gaze can improve accuracy, robustness and interpretability of the CAD system. You can read our paper and code for more detail. In short, we force the network to look at area where radiologist looked.

![image-20210923151706030](img/guided_attention.png)

## Multi-task

Karargyris et al.[1] offers a multi-task framework to utlize eye gaze information as the following figure demonstrated. The backbone have two task: 1. classfication and 2. predict human visual attention. Similiar framework can also be found at [2] where they use mouse instead of eye gaze.

![image-20210923144739581](img/Karargyris.png)

## Reference

1. A.  Karargyris,  S.  Kashyap,  I.  Lourentzou,  J.  T.  Wu,  A.  Sharma,  M.  Tong,  S.  Abedin,D.  Beymer,  V.  Mukherjee,  E.  A.  Krupinskiet  al.,  “Creation  and  validation  of  a  chest  x-ray dataset with eye-tracking and report dictation for ai development,”Scientific data, vol. 8,no. 1, pp. 1–18, 2021.

2. L.Li,M.Xu,X.Wang,L.Jiang,andH.Liu,“Attentionbasedglaucoma detection: A large-scale database and cnn model,” in *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, 2019, pp. 10 571–10 580.

   
