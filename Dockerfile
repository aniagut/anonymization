FROM python:3.9.12

#Expose port 8080
EXPOSE 8080

#Optional - install git to fetch packages directly from github
RUN apt-get update && apt-get install -y git build-essential libgtk-3-dev libboost-all-dev freeglut3-dev cmake libopenblas-dev libgl1-mesa-glx tesseract-ocr libtesseract-dev libtesseract4 tesseract-ocr-all

RUN curl -L -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda install numpy pyyaml scipy ipython mkl && \
     /opt/conda/bin/conda install -c soumith magma-cuda90

COPY environment.yml .
RUN conda env create -f environment.yml

RUN conda activate env

#Copy all files in current directory into app directory
COPY . /app

#Change Working Directory to app directory
WORKDIR /app

#Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "Main_page.py", "--server.port=8080", "--server.address=0.0.0.0"]