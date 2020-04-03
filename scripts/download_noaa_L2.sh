#/usr/bin/sh

product=ABI-L2-FDCF;
year=2019;
doy_min=180;
doy_max=270;

mkdir /nobackupp10/tvandal/data/goes16/$product/;
mkdir /nobackupp10/tvandal/data/goes16/$product/$year;

for i in $(seq $doy_min $doy_max); do
	aws s3 cp s3://noaa-goes16/$product/$year/$i/ /nobackupp10/tvandal/data/goes16/$product/$year/$i/ --recursive; 
done;
