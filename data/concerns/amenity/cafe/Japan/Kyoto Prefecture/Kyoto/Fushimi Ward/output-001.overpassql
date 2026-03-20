[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Fushimi Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
