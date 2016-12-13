## Running SoilGenerate

### Install GLPK

This application uses Python PuLP to interface with GLPK's linear programming solver. On Ubuntu, install GLPK with:

```
sudo apt-get install python-glpk
sudo apt-get install glpk-utils
```

### Setup Virtual Environment
```
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

### Run SoilGenerate
```
python3 -m soilgenerate
```

## Summary

Cultivated fruits and vegetables require optimal soil conditions for high yields. In a traditional sense, soil optimization focuses on maintaining quantities of chemical nutrients vital to plant growth; however, farmland must also contain sufficient organic matter in soil to store these nutrients. This rich organic matter, called humus, also stores water and beneficial microorganisms. 

Because sandy soil lacks humus, making sandy farmland usable requires physically bringing in organic matter in an extremely labor intensive process.

A possible solution to the quick fix of physically adding organic matter is preparing farmland over time by planting fast-growing plants which shed roots and leaves at a rapid rate, thereby increasing organic matter in the soil gradually. Using data on native plant growth rates and optimal growing conditions [1] and processed remote sensing soil data [2], SoilGenerate is a software implementation of Simplex which constrains the financial cost of purchasing seeds [3] for a user specified area to maximize hypothetical plant growth based on soil conditions. 

Resources :

[1] USDA Plant Database http://plants.usda.gov/adv_search.html

[2] USDA Remote Sensing Soil Database http://websoilsurvey.sc.egov.usda.gov/  

[3] Seed Vendor for Pricing https://www.sheffields.com/

