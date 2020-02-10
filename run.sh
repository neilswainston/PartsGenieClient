pip install -r requirements.txt 

export PYTHONPATH=$PYTHONPATH:.

python parts_genie/client.py https://parts.synbiochem.co.uk/ data/sbol.xml 37762 out