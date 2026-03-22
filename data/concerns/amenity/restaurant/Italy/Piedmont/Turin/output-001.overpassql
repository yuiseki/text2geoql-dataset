[out:json][timeout:30];
area["name:en"="Piedmont"]->.outer;
area["name:en"="Turin"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;