[out:json][timeout:30];
area["name:en"="Bangkok"]->.outer;
area["name:en"="Bangkok"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;