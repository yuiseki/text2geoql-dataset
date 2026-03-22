[out:json][timeout:30];
area["name:en"="Hiroshima Prefecture"]->.outer;
area["name:en"="Hiroshima"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;