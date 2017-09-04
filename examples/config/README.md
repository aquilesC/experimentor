# Example configuration folder for the Experimentor Package#

This folder holds the most important files for configuring the behavior of the experiment. There are two kind of files, YAML files and pure python. 

YAML files define parameters for the experiment that are thought to be customized by the user; for example the wavelength of a laser, the name of the devices plugged to a DAQ card, etc. 

Python files are thought to be used as a module for default values. Every time there is the doubt regarding a constant, for example if the NI-DAQ should acquire in the trigger falling or rising, or if there are problems with buffer sizes, etc.

### devices.yml ### 
Hold all the devices information, be it a laser connected through serial or a DAQ. **Very Important:** Every device needs a name and it has to be unique. Spaces are OK, since it is formatted as a Python string. The entire program calls devices by its name, so beware! 

The **driver** section holds the path of the driver in the form of a Python import plus a specification of a class. For example:
```python
model.daq.ni/ni
```    
This would import the class ni from the package model.daq.ni . Beautifully enough, this also works for packages anywhere in the Python environment.

### sensors.yml ###
This file specifies the sensors relevant to the experiment. Sensors are those devices such as photodiodes that are not connected directly to the computer but that are connected to a ADQ. For simplicity, sensors are also the properties of devices that are connected directly to the computer. For example, the power measured by a powermeter can be specified in this file. 

### actuators.yml ###
Actuators are all the devices that can modify the experiment. For example a piezo stage is an actuator. In the same fashion that with sensors, if a device plugged directly to the PC has parameters that can be changed, those have to be defined in this file. For example, the position of a stepper motor that is controlled directly through the USB connection.
 
### devices_defaults.yml ###
Holds the values at which a device will be initialized. In `experiment.base_experiment` there is a method called `initialize_devices` that will look if there are defaults established. They will be applied directly to the driver, through a `setattr`; therfore, if in defaults the _wavelength_ is specified, the driver should have a _wavelenegth_ property. 
 
### measurement.yml ###
This yaml file holds the information of the measurement to be done. Ideally it sets up different steps, like initialization, scan, finalization, but it is very flexible and is used as a starting point for designing experiments. 
 
The file _measurement_ was done with a particular setup in mind, but the file _example_confocal_ was done with a confocal microscope in mind. These files will be interpreted by the classes defined in `measurement`, to which the user should refer for further information. 
 
 ## TO DO ## 
- The way things things work with the devices is confusing, since there are both devices connected to the PC and devices connected to other devices (i.e. a photodiode connected to a DAQ, for instance.)
    - [X] TODO: Define devices in a nested fashion
    - [X] TODO: Have lower level files where settings that a normal user shouldn't change separated.
    - [X] TODO: Config files should be placed outside the package folder.
- A way of generalizing the code would be to define general (and strict) properties for the devices. For example, a value can be set to a daq port, but also to the wavelength of a laser. A value can be read from an oscilloscope or from a voltmeter, etc.
    - [X] TODO: For each device define properties that can be `set` and properties that can be `get`.
    - [ ] TODO: Define properties that can be made `ramp` or that are `bool`
    - [ ] TODO: Define a skeleton file of properties that allows to check for the completness of the definitions before running the program, and would warn the user of a badly stated devices or experiment file.
    - [ ] TODO: Check if lantz has a way of retrieving the limits of properties, to avoid declaring them twice.