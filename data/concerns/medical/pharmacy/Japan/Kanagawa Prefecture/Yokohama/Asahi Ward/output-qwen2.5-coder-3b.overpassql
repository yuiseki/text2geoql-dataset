[out:json][timeout:30];
area["name:en"="Asahi Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["amenity"~"pharmacy"](area.inner)(area.outer);
);
out geom;
