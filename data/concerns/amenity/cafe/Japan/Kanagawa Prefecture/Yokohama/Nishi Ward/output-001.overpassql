[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
