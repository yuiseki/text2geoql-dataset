[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Geumcheon-gu"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
