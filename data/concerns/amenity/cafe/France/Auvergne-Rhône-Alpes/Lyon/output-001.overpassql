[out:json][timeout:30];
area["name:en"="Auvergne-Rhône-Alpes"]->.outer;
area["name:en"="Lyon"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;