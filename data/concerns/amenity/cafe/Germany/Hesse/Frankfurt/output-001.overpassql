[out:json][timeout:30];
area["name:en"="Hesse"]->.outer;
area["name:en"="Frankfurt"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;