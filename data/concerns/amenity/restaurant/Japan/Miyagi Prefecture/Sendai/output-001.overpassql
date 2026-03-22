[out:json][timeout:30];
area["name:en"="Miyagi Prefecture"]->.outer;
area["name:en"="Sendai"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;