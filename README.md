# National Ground-Level NO<sub>2</sub> Predictions Via Satellite Imagery Driven Convolutional Neural Networks

Code for the manuscript entitled, "National Ground Level NO<sub>2</sub> Predictions Via Satellite Imagery Based Convolutional Neural Networks," towards more accurate, low-cost NO<sub>2</sub> modeling using modern deep learning techniques.

As of now, the code contains an example of a single train test split for annual prediction, as well as sample Google Earth Engine scripts to retrieve the NO<sub>2</sub> data and population density data.

# Files & Folders

- "example CNN.ipynb": notebook to run annual prediction task.
- "earth engine data collection/TROPOMI.py": Python file to collect NO<sub>2</sub> data and aggregate into daily averages.
- "earth engine data collection/population density.py": Python file to collect population density bounding boxes.
- data: folder containing all necessary dictionaries to run "example CNN.ipynb."

# Package Dependencies

- PyTorch
- Pandas
- NumPy
- Scikit-Learn
- tqdm
- torchmetrics
- Earth Engine
- datetime
- logging
- multiprococessing
- retry
- psutil
- os
- urllib
