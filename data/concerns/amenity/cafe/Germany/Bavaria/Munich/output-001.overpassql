[out:json][timeout:30];
area["name:en"="Bavaria"]->.outer;
area["name:en"="Munich"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;