[out:json][timeout:30];
area["name:ja"="横浜市"]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["amenity"~"bicycle_rental"](area.inner)(area.outer);
);
out geom;
