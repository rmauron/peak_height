# Peak Height
As part of a fellow student's master's work, the height of peak series had to be measured. I ensured to facilitate the task with this script that automatically indicates these distances without the need to manually manipulate the data beforehand.

## Context
Real-time detection and quantification of metabolites generated through bioproduction are a key aspect in biologics manufacturing and product purification. Through the implementation of a novel protein quantification unit, this information can be used to optimize those processes. In the context of raw data analysis given by the device, a reliable and automated solution is needed to accurately deliver this information. The software described below does exactly that, by calculating the difference in response associated with a shift in the light incidence, with each shift corresponding to a measurement. This specific change in response is necessary to associate each sample analyzed to its respective product concentration.

## Prerequisites
All you need is to have a directory with the script ```plot_peak_height.py```, specify your path to the directory in line 10 of the script.

Organize your project directory in the following manner:

```
peak_height_project
├── README.md
├── data
│   ├── Offline_test1_SN_7_1.txt
│   ├── Offline_test1_SN_7_2.txt
│   ├── Offline_test1_SN_7_3.txt
│   └── Offline_test1_SN_7_4.txt
└── plot_peak_height.py
```

with all the data files in the data repository and the script.

Once you run the script, a folder ```output``` is automatically generated and stores a ```csv``` repository with a csv file for peak heights of each sample in data precising the position of the peak difference on the x-axis and the corresponding peak height. Two other repositories are also created in ```output```, ```plot_distance``` that stores figures with distance printed on it and ```plot_only``` that stores the figures without annotation.

```
peak_height_project
├── README.md
├── data
│   ├── Offline_test1_SN_7_1.txt
│   ├── Offline_test1_SN_7_2.txt
│   ├── Offline_test1_SN_7_3.txt
│   └── Offline_test1_SN_7_4.txt
│
├── output
│   ├── csv
│   │   ├── Offline_test1_SN_7_1.csv
│   │   ├── Offline_test1_SN_7_2.csv
│   │   ├── Offline_test1_SN_7_3.csv
│   │   └── Offline_test1_SN_7_4.csv
│   │
│   ├── plot_distance
│   │   ├── Offline_test1_SN_7_1dist.png
│   │   ├── Offline_test1_SN_7_2dist.png
│   │   ├── Offline_test1_SN_7_3dist.png
│   │   └── Offline_test1_SN_7_4dist.png
│   │
│   └── plot_only
│       ├── Offline_test1_SN_7_1.png
│       ├── Offline_test1_SN_7_2.png
│       ├── Offline_test1_SN_7_3.png
│       └── Offline_test1_SN_7_4.png
│
└── plot_peak_height.py
```

At this point, the work is done.


## Parameters
This software is designed to work seamlessly with your data structure, requiring minimal parameter changes. 
However, note that in the script ```plot_peak_height.py``` you will need to specify your working directory.

* Line smoothing, line 60 <br>
You can change the ```sigma``` value, which is the standard deviation for Gaussian kernel. Increasing the sigma value will result in a smoother line. This might be necessary when your measurement has many oscillations that you don't want to count.

* Lower limit for peak detection, line 67 <br>
You can change the lower limit from the y-axis from which you want to detect peak maxima. By default, it considers peaks above the threshold ```-2000```.

* Minimum vertical distance for peak detection, line 94 <br>
You can specify the minimum vertical distance you want to consider between two consecutive maxima to count them as a significant peak. By default, the minimum vertical distance is set to ```60```.


## Final note
I am always looking for ways to improve this project, so please feel free to contact me with any suggestions or feedback through [Linkedin](https://www.linkedin.com/in/raphael-mauron/). Your input is greatly appreciated!