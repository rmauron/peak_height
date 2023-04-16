# peak_height

As part of a fellow student's master's work, the height of peak series had to be measured. I ensured to facilitate the task with this script that automatically indicates these distances without the need to manually manipulate the data beforehand.

## Prerequisities
All you need is to have a directory with the script "plot_peak_height.py", specify your path to the directory in line 9 of the script.

Organize your project directory in the following manner:

peak_height_project
├── README.md
├── data
│   ├── Offline_test1_SN_7_1.txt
│   ├── Offline_test1_SN_7_2.txt
│   ├── Offline_test1_SN_7_3.txt
│   └── Offline_test1_SN_7_4.txt
└── plot_peak_height.py

with all the data files in the data repository and the script.

Once you run the script, a folder "output" is automatically generated and stores every plot with the same name as the data inputs:

peak_height_project
├── README.md
├── data
│   ├── Offline_test1_SN_7_1.txt
│   ├── Offline_test1_SN_7_2.txt
│   ├── Offline_test1_SN_7_3.txt
│   └── Offline_test1_SN_7_4.txt
├── output
│   ├── Offline_test1_SN_7_1.png
│   ├── Offline_test1_SN_7_2.png
│   ├── Offline_test1_SN_7_3.png
│   └── Offline_test1_SN_7_4.png
└── plot_peak_height.py

At this point, the work is done.