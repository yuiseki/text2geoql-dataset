[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangbuk-gu"]->.inner;
(
  nwr["amenity"="pharmacy"](area.inner)(area.outer);
);
out geom;
