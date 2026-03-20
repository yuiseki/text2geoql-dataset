[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Seya Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
