[out:json][timeout:30];
area["name:ja"="さいたま市"]->.outer;
area["name:ja"="埼玉県"]->.inner;
(
  nwr["amenity"~"car_rental"](area.inner)(area.outer);
);
out geom;
