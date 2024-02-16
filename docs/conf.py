import sys

sys.path.append('..')

import visca_over_ip

project = 'visca_over_ip'
author = 'Yook74 and misterhay'
version = visca_over_ip.__version__

extensions = ['sphinx.ext.autodoc']
html_theme = 'nature'
html_sidebars = {'**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html']}
