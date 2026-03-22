[out:json][timeout:30];
area["name:en"="Bangkok"]->.outer;
area["name:en"="Bangkok"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;