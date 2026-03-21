[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["amenity"~"hospital|clinic"](area.inner)(area.outer);
);
out geom;
