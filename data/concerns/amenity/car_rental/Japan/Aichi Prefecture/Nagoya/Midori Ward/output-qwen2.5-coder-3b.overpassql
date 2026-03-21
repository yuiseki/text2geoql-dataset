[out:json][timeout:30];
area["name:ja"="名古屋市"]->.outer;
area["name:ja"="愛知県"]->.inner;
(
  nwr["amenity"~"car_rental"](area.inner)(area.outer);
);
out geom;
