[out:json][timeout:30];
area["name:en"="Valencia"]->.outer;
area["name:en"="Valencia"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;