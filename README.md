# Normative Neurodevelopment: Cross-sectional predictive modeling
<!-- This repository includes code used to analyze the relationship between dimensional psychopathology phenotypes and deviations from normative neurodevelopment in the Philadelphia Neurodevelopmental Cohort. -->

# Environment build

    conda create -n neurodev_cs_predictive python=3.7
    conda activate neurodev_cs_predictive

    # Essentials
    pip install jupyterlab ipython pandas numpy seaborn matplotlib nibabel glob3 nilearn ipywidgets
    pip install jupyter_contrib_nbextensions && jupyter contrib nbextension install

	# Statistics
	pip install scipy statsmodels sklearn pingouin pygam brainspace shap

	# Pysurfer for plotting
	pip install mayavi
	pip install PyQt5
	jupyter nbextension install --py mayavi --user
	jupyter nbextension enable --py mayavi --user
	jupyter nbextension enable --py widgetsnbextension
	pip install pysurfer

    cd /Users/lindenmp/Dropbox/Work/ResProjects/neurodev_cs_predictive
    conda env export > environment.yml
	pip freeze > requirements.txt

# Environment build (cubic, home)

    conda create -n neurodev_cs_predictive python=3.7
    conda activate neurodev_cs_predictive

    # Essentials
    pip install ipython pandas numpy glob3

	# Statistics
	pip install scipy statsmodels sklearn pingouin

	cd /cbica/home/parkesl/miniconda3/envs/neurodev_cs_predictive/
    conda env export > environment.yml
	pip freeze > requirements.txt


<!-- # Code

In the **code** subdirectory you will find the following Jupyter notebooks and .py scripts:
1. Pre-normative modeling scripts:
- `get_train_test.ipynb`
	- Performs initial ingest of PNC demographic data, participant exclusion based on various quality control.
	- Produces Figures 2A and 2B.
	- Designates train/test split.
- `compute_node_metrics.ipynb`
	- Reads in neuroimaging data.
	- Sets up feature table of regional brain features.
- `clean_node_metrics.ipynb`
	- Performs nuisance regression on feature table.
- `prepare_normative.ipynb`
	- Prepares input files for normative modeling.

2. Run normative modeling:
- `run_normative_local.py`
	- Runs primary normative models on local machine.
- `cluster/run_normative_perm.sh`
	- Submits each of the permuted normative models to the cluster as a separate job

3. Results:
- `results_s1.ipynb`
	- Produces Figure 2C
- `results_s2.ipynb`
	- Produces Figures 3 and 4
- `results_s3.ipynb`
	- Produces Figure 5 -->
