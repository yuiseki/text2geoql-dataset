[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangseo-gu"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
