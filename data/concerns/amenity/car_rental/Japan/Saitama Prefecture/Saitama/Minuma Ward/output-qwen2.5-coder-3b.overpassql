[out:json][timeout:30];
area["name:ja"="埼玉県"]->.outer;
area["name:ja"="さいたま市"]->.inner;
(
  nwr["amenity"~"car_rental"](area.inner)(area.outer);
);
out geom;
