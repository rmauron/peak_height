# Peak Height

As part of a fellow student's master's work, the height of peak series had to be measured. I ensured to facilitate the task with this script that automatically indicates these distances without the need to manually manipulate the data beforehand.

## Prerequisities
All you need is to have a directory with the script "plot_peak_height.py", specify your path to the directory in line 10 of the script.

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
