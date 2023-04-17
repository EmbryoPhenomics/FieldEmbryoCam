sudo apt-get install -y \
     python3 \
     python3-dev \
     python3-pip \
     python3-numpy 

sudo python3 -m pip install cython \ numpy \ math \ picamera \ python-smbus 
sudo python3 -m pip install scipy \ scikit-image \ setuptools \ tqdm \ more_itertools \ natsort \ picamera
sudo apt-get install -y python3-opencv
sudo apt-get install libatlas-base-dev

git clone https://github.com/bluerobotics/tsys01-python
cd tsys01-python
sudo python3 setup.py install

git clone https://github.com/bluerobotics/ms5837-python.git
cd ms5837-python
sudo python3 setup.py install
