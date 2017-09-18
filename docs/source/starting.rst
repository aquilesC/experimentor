Starting to use the Experimentor
================================

The package provides the basic classes and functions to communicate with devices and plan experiments. The package was designed to impose a workflow that guarantees the user will be able to plan an experiment from start to finish.

Experimentor is packaged with the folder containing the main code, i.e. the package itself, and a folder of examples that show some cases of how the program can be used.

The logic behind Experimentor is that the parameters that a user has to set for performing an experiment are layed out in YAML files. So, for example, the port at which a photodiode is plugged is defined in a yaml file. The steps of the experiment are also layed out in a YAML file, in order to make clear what needs to be set, changed, scanned, etc. These files are then read and passed to a special class of Experimentor.

Experimentor defines only general classes and methods that enable the user to define a common approach to the problems, however every experiment is different and has to be developed by each user. The examples folder are a good starting point for lerning, as well as the explanations found hereafter.

The steps needed to make an experiment using the Experimentor are as follow:

   First one has to define which devices are going to be used and make a YAML file for them.
   Then, the steps of the experiment are layed out in another YAML file.
   A class based on Experimentor is written, with methods for every step layed out in the YAML file.
   In principle a GUI can be built to modify the parameters passed to the experimentor class.

Each step is thought in order to force the user to be in control of his/her experiment and not to rely on preconceived concepts that can be far from how the setup actually works.

Defining devices, sensors and actuators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every experiment should start by defining what devices, sensors and actuators are going to be used. The general structure is that devices communicate with the computer, while sensors and actuators are plugged into devices. For example an acquisition card such as an oscilloscope is a *device*. A photodiode connected to it is a *sensor*, while a piezo stage connected to the output of a function generator is an *actuator*.

In the same fashion, a tunable laser is a device and the wavelength is an actuator. In this way the same structure of programs can be preserved throughout different projects. This is specially handy when developing GUIs, since it enables the iteration through all sensors or all actuators of a given device.

Devices, sensors and actuators are defined through YAML files. The examples folder contains some general files that show how to do it. Generally speaking it would look like something like this::

   NI-DAQ:
     name: NI-DAQ
     type: daq
     model: ni
     number: 2
     driver: experimentor.models.daq.ni/ni
     connection:
       type: daq
       port: 2
     trigger: external
     trigger_source: PFI0

No field is required a priory, but giving a name is highly recommended. All the other fields are self explanatory. Sensors and actuators are defined in a similar way::

   NI-DAQ:
     Stage 1:
       port: 1
       type: analog
       mode: output
       description: Example analog Out
       calibration:
         units: um  # Target units, starting from volts. The calibration thus would be: device_value (true units) = slope*volts+offset
         slope: 1
         offset: 0
       limits:
         min: 0um
         max: 10um
       default: 5um

Note that the first key is the device to which the actuator is plugged. If defining actuators or sensors in the same file, they should be nested according to the device to which they are plugged. The first key afterwards is the name of the device and should be unique; if not, it will be overriden by the latest sensor/actuator loaded. The two more important pieces of information are the calibration and limits. The first explains the program how to convert from volts (the natural units of any ADQ) to the units of the actuator/sensor. The latter is for safety purposes and to maximize the convertion resolution of the DAQ that support setting variable gains.

None of the keys specified here are mandatory, but common sense dictates that the ones shown in the example are the minimum required ones for an experiment.

Defining the Experiment
~~~~~~~~~~~~~~~~~~~~~~~
The experiment, following the scheme developed for devices, sensors and actuators, is layed out in a YAML file. When writing it, the user has to keep in mind what are the parameters that need to be used, the kind of measurements that have to be achieved, etc. At this stage it is only a matter of thinking, the real logic and communication with devices will come later.