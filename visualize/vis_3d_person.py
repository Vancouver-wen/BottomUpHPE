import os
import sys
import io

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from utils.imageConcat import show_multi_imgs
from association.openpose_detection import SKEL19DEF

# define a function which returns an image as numpy array from figure
def get_img_from_fig(fig, dpi=180):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def vis_3d_person(
        index,
        image_list,
        cam_params,
        persons,
        definition=SKEL19DEF,
        save_name="no_hier"
    ):
    images=[cv2.imread(image_path) for image_path in image_list]
    for image,cam_param in list(zip(images,cam_params)):
        for person_id in persons:
            person=persons[person_id]
            for paf in definition.paf_dict:
                kpt3da,kpt3db=person[paf[0]],person[paf[1]]
                if kpt3da[-1]<0 or kpt3db[-1]<0:
                    continue
                kpt3ds=np.array([kpt3da,kpt3db])[:,:3]
                kpt2ds,_=cv2.projectPoints(
                    objectPoints=kpt3ds.T,
                    rvec=np.array(cam_param['R']),
                    tvec=np.array(cam_param['t']),
                    cameraMatrix=np.array(cam_param['K']),
                    distCoeffs=np.array(cam_param['dist'])
                )
                kpt2ds=kpt2ds.squeeze().astype(np.int32)
                image=cv2.line(
                    img=image,
                    pt1=kpt2ds[0],
                    pt2=kpt2ds[1],
                    color=(0,0,255),
                    thickness=2
                )
    frame=show_multi_imgs(
        scale=1,
        imglist=images,
        order=(2,3)
    )
    # p frame.shape 
    # (4100, 6150, 3)
    fig=plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.view_init(elev=30.0, azim=index*60/360-180)
    ax.set_xlim(-5, 5) 
    ax.set_ylim(-5, 5) 
    ax.set_zlim(0, 5) 
    for person_id in persons:
        person=persons[person_id]
        for paf in definition.paf_dict:
            kpt3da,kpt3db=person[paf[0]],person[paf[1]]
            if kpt3da[-1]<0 or kpt3db[-1]<0:
                continue
            kpt3ds=np.array([kpt3da,kpt3db])[:,:3]
            ax.plot(
                kpt3ds[:,0],
                kpt3ds[:,2],
                kpt3ds[:,1],
                color='red',
                linewidth=1
            )
    image=get_img_from_fig(
        fig=fig,
        dpi=1000
    )
    fig.clear()
    plt.close() 
    height=image.shape[0]
    ratio=4100/height
    image=cv2.resize(image,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA)
    frame=cv2.hconcat([frame,image])
    frame=cv2.resize(frame,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'./myvis/{save_name}.jpg',frame)
    return frame