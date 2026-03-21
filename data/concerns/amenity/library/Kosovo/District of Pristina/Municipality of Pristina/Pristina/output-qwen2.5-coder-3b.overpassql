[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
area["name:en"="Kosovo"]->.inner;
(
  nwr["amenity"~"library"](area.inner)(area.outer);
);
out geom;
