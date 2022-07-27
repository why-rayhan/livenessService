#
FROM tensorflow/tensorflow:2.3.0-gpu

# 
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
#RUN lsb_release -a
RUN  apt-get install -y wget
RUN apt-key del 7fa2af80
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb
RUN dpkg -i cuda-keyring_1.0-1_all.deb
#RUN ls /etc/apt/sources.list.d/*
#RUN cat /etc/apt/sources.list.d/cuda-ubuntu1804-x86_64.list
#RUN cat /etc/apt/sources.list.d/cuda.list
#RUN cat /etc/apt/sources.list.d/nvidia-ml.list
RUN rm /etc/apt/sources.list.d/cuda.list
# RUN grep -l "nvidia.github.io" /etc/apt/sources.list.d/* | grep -vE "/nvidia-container-toolkit.list\$"
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip list
#
COPY ./model /code/model
COPY ./evaluation.py /code/evaluation.py

#
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "evaluation.py"]