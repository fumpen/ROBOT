This directory contains source code that might be helpful when solving
exercise 5. We provide both C++ and Python versions of this code.

The only file that needs editing to create a working system
is exercise5.cc or exercise5.py, but it is recommended to have a brief look at the rest
of the source code. In particular it is recommended to look at particle.[cc|h|py]
to see how particles are represented.

The files exercise5.cc and exercise5.py was created by simply removing parts of a 
functioning program and replacing these parts by lines saying:
  //XXX: You do this
So look for 'XXX' to see where you should concentrate your efforts.

The program uses the camera class found in camera.[cc|h|py] to access the camera and do the image
analysis. This class requires a file containing camera calibration parameters in YAML format. You can calibrate
your own camera using the camera_calibrator found in Absalon under OpenCV.

The main C++ project for exercise5 can be build using the make command. Just type
make

Alternatively, CMake can be used like this:
mkdir build
cd build/
cmake ..
make

This auto-generates makefile's or you can use the generator facility of cmake to generate project files for your favourite IDE. 

If you're having problems understanding the code, don't hesitate to contact me.

Kim Steenstrup Pedersen, september 9, 2015.
Søren Hauberg, august 21st, 2006.
