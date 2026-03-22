[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;