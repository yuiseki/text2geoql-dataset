[out:json][timeout:30];
area["name:en"="Piedmont"]->.outer;
area["name:en"="Turin"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;