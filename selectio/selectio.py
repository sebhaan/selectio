"""
Multi-model Feature Importance Scoring and auto Feature Selection.
------------------------------------------------------------------- 

This Python package returns multiple feature importance scores, feature ranks,
and automatically suggests a feature selection based on the majority vote of all models.

## Models

Currently the following six models for feature importance scoring are included:
- Spearman rank analysis (see 'models.spearman')
- Correlation coefficient significance of linear/log-scaled Bayesian Linear Regression (see 'models.blr')
- Random Forest Permutation test (see 'models.rf.py')
- Random Decision Trees on various subsamples of data (see 'models.rdt.py')
- Mutual Information Regression (see 'models.mi')
- General correlation coefficients (see 'models.xicor')

## Usage

The feature selection score can be either computed directly using the class Fsel, or can be called directly 
with more functionality (including preprocessing and plotting) using a settings yaml file:
python selectio.py -s fname_settings

User settings such as input/output paths and all other options are set in the settings file 
(Default filename: settings_featureimportance.yaml) 
Alternatively, the settings file can be specified as a command line argument with: 
'-s', or '--settings' followed by PATH-TO-FILE/FILENAME.yaml 
(e.g. python selectio.py -s settings/settings_featureimportance.yaml).
"""
import os
import sys
import yaml
import shutil
import argparse
import datetime
from types import SimpleNamespace  
import numpy as np
import pandas as pd
import importlib

# import some custom plotting utility functions
from utils import plot_correlationbar, plot_feature_correlation_spearman

# import all models for feature importance calculation
from models import __all__ as _modelnames
_list_models = []
for modelname in _modelnames:
	module = importlib.import_module('models.'+modelname)
	_list_models.append(module)

# Settings for default yaml filename
_fname_settings = 'settings_featureimportance.yaml'


class Fsel:
	"""
	Auto Feature Selection
	"""
	def __init__(self, X, y):
		
		self.X = X
		self.y = y

		self.nmodels = len(_modelnames)
		self.nfeatures = X.shape[1]

		# Initialise pandas dataframe to save results
		self.dfmodels = pd.DataFrame(columns=['score_' + modelname for modelname in _modelnames])


	def score_models(self):
		"""
		Calculate feature importance for all models and select features

		Return:
			dfmodels: pandas dataframe with scores for each feature
		"""
		# Loop over all models and calculate normalized feature scores
		count_select = np.zeros(self.nfeatures).astype(int)
		for i in range(self.nmodels):
			model = _list_models[i]
			modelname = _modelnames[i]
			print(f'Computing scores for model {modelname}...')
			corr = model.factor_importance(self.X, self.y, norm = True)
			self.dfmodels['score_' + modelname] = np.round(corr, 4)
			# Calculate which feature scores accepted
			woe = self.eval_score(corr)
			self.dfmodels['woe_' + modelname] = woe
			count_select += woe
			print(f'Done, {woe.sum()} features selected.')
		
		# Select features based on majority vote from all models:
		select = np.zeros(self.nfeatures).astype(int)
		select[count_select >= self.nfeatures/2] = 1
		self.dfmodels['selected'] = select
		return self.dfmodels


	def eval_score(self, score, woe_min = 0.05):
		"""
		Evaluate multi-model feature importance scores and select features based on majority vote

		Input:
			score: 1dim array with scores
			woe_min: minimum fractional contribution to total score (default = 0.05)
		Return:
			woe: array of acceptance (1 = accepted, 0 = not)
		""" 
		sum_score = score.sum()
		min_score = sum_score * woe_min
		woe = np.zeros_like(score)
		woe[score >= min_score] = 1
		return woe.astype(int)


def main(fname_settings):
	"""
	Main function for running the script.

	Input:
		fname_settings: path and filename to settings file
	"""
	# Load settings from yaml file
	with open(fname_settings, 'r') as f:
		settings = yaml.load(f, Loader=yaml.FullLoader)
	# Parse settings dictinary as namespace (settings are available as 
	# settings.variable_name rather than settings['variable_name'])
	settings = SimpleNamespace(**settings)

	# Verify output directory and make it if it does not exist
	os.makedirs(settings.outpath, exist_ok = True)

	# Read data
	data_fieldnames = settings.name_features + [settings.name_target]
	df = pd.read_csv(os.path.join(settings.inpath, settings.infname), usecols=data_fieldnames)

	# Verify that data is cleaned:
	assert df.select_dtypes(include=['number']).columns.tolist().sort() == data_fieldnames.sort(), 'Data contains non-numeric entries.'
	assert df.isnull().sum().sum() == 0, "Data is not cleaned, please run preprocess_data.py before"

	# Generate Spearman correlation matrix for X
	print("Calculate Spearman correlation matrix...")
	plot_feature_correlation_spearman(df[data_fieldnames].values, data_fieldnames, settings.outpath, show = False)

	X = df[settings.name_features].values
	y = df[settings.name_target].values

	# Generate feature importance scores
	fsel = Fsel(X,y)
	dfres = fsel.score_models()

	dfres['name_features'] = settings.name_features
	print('Features selected: ', dfres.loc[dfres.selected == 1, 'name_features'])
	
	# Save results as csv
	dfres.to_csv(os.path.join(settings.outpath, 'feature-importance_scores.csv'), index_label = 'Feature_index')

	# initialise array for total score across all models
	scores_total = np.zeros(X.shape[1])
	# Plot scores
	print("Generating score plots..")
	for i in range(len(_modelnames)):
		modelname = _modelnames[i]
		try:
			model_label = _list_models[i].__name__
			model_fullname = _list_models[i].__fullname__
		except:
			model_label = modelname
			model_fullname = modelname
		scores = dfres['score_' + modelname].values
		woe = dfres['woe_' + modelname].values
		plot_correlationbar(scores, settings.name_features, settings.outpath, f'{model_label}-feature-importance.png', name_method = model_fullname, show = False)

		# Add to total scores
		scores_total += scores * woe
	# plot total score
	scores_total /= np.sum(scores_total)
	plot_correlationbar(scores_total, settings.name_features, settings.outpath, 'Combined-feature-importance.png', name_method = 'Combined Model Score', show = False)


if __name__ == '__main__':
	# Parse command line arguments
	parser = argparse.ArgumentParser(description='Calculating feature importance.')
	parser.add_argument('-s', '--settings', type=str, required=False,
						help='Path and filename of settings file.',
						default = os.path.join('./settings',_fname_settings))
	args = parser.parse_args()

	# Log computational time
	datetime_now = datetime.datetime.now()
	# Run main function
	main(args.settings)
	# print out compute time of main function in seconds
	print('Total computational time: {:.2f} seconds'.format((datetime.datetime.now() - datetime_now).total_seconds()))