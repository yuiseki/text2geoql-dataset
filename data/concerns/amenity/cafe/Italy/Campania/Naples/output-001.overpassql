[out:json][timeout:30];
area["name:en"="Campania"]->.outer;
area["name:en"="Naples"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;