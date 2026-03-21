[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
(
  nwr["amenity"="bicycle_rental"](area.outer);
);
out geom;
