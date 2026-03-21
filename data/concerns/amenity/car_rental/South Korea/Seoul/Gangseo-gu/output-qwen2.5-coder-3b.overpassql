[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangseo-gu"]->.inner;
(
  nwr["amenity"="car_rental"](area.inner)(area.outer);
);
out geom;
