# Community_Inclusion_Currencies
Repository for Complex Systems model of the Grassroots Economics Community Inclusion Currency project. Modeling is built in [cadCAD](https://cadcad.org/). 

## What is cadCAD?
cadCAD (complex adaptive dynamics Computer-Aided Design) is a python based modeling framework for research, validation, and Computer Aided Design of complex systems. Given a model of a complex system, cadCAD can simulate the impact that a set of actions might have on it. This helps users make informed, rigorously tested decisions on how best to modify or interact with the system in order to achieve their goals. cadCAD supports different system modeling approaches and can be easily integrated with common empirical data science workflows. Monte Carlo methods, A/B testing and parameter sweeping features are natively supported and optimized for.

See [cadCAD on Github](https://github.com/BlockScience/cadCAD/tree/master/tutorials) for some tutorials on how to use cadCAD.


## Reproducibility
In order to reperform this code, we recommend the researcher use the following link to download https://www.anaconda.com/products/individual to download Python 3.7.To install the specific version of cadCAD this repository was built with, run the following code:
```conda create -n cic python=3.7 -y```
```conda activate cic```

To download the specific version of this code, run the following command in your command line:

```git clone -b paper https://github.com/BlockScience/Community_Inclusion_Currencies.git``` 

```pip install -r requirements.txt```

Then run ```cd Community_Inclusion_Currencies``` to enter the repository. Finally, run ```jupyter notebook``` to open a notebook server to run the various notebooks in this repository. 


## Simulations

### Theory work
[Click here](https://nbviewer.jupyter.org/github/BlockScience/Community_Inclusion_Currencies/blob/master/BondingCurve/cic_initialization.ipynb)

### Subpopulation initialization 
[Click here](https://nbviewer.jupyter.org/github/BlockScience/Community_Inclusion_Currencies/blob/master/SubpopulationGenerator/Subpopulation_Construction.ipynb)

### Simulation work
[Click here](https://nbviewer.jupyter.org/github/BlockScience/Community_Inclusion_Currencies/blob/master/Simulation/CIC_Network_cadCAD_model.ipynb)

### Parameter sweep 
[Click here](https://nbviewer.jupyter.org/github/BlockScience/Community_Inclusion_Currencies/blob/master/Simulation_param/CIC_Network_cadCAD_model_params_Template.ipynb)

