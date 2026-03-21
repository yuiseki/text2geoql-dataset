[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Guro-gu"]->.inner;
(
  nwr["amenity"="drinking_water"](area.inner)(area.outer);
);
out geom;
