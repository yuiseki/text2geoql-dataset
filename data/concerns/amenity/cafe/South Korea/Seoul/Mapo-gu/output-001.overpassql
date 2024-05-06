[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Mapo-gu"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
