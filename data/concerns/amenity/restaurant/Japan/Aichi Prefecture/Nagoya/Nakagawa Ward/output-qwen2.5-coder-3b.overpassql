[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Aichi Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
