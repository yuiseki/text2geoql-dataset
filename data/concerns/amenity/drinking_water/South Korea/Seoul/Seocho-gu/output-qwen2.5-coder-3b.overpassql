[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
(
  nwr["amenity"="drinking_water"](area.outer);
);
out geom;
