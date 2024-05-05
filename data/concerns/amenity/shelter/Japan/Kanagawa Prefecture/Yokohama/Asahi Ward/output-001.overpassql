[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Asahi Ward"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
